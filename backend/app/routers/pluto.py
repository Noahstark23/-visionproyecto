import uuid
import httpx
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.channel import Channel
from app.models.category import Category

router = APIRouter(prefix="/api/pluto", tags=["pluto"])

PLUTO_API = "https://api.pluto.tv/v2/channels"


async def fetch_pluto_channels() -> list:
    client_id = str(uuid.uuid4())
    now = datetime.utcnow()
    stop = now + timedelta(hours=4)
    params = {
        "appVersion": "5.3.0",
        "deviceType": "web",
        "deviceVersion": "1.0.0",
        "clientID": client_id,
        "clientModelNumber": "1",
        "serverSideAds": "true",
        "start": now.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "stop": stop.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
    }
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(PLUTO_API, params=params)
        response.raise_for_status()
        return response.json()


def extract_stream_url(channel_data: dict, client_id: str) -> str:
    stitched = channel_data.get("stitched", {})
    for url_obj in stitched.get("urls", []):
        url = url_obj.get("url", "")
        if url and "m3u8" in url:
            return url
    channel_id = channel_data.get("_id", "")
    if channel_id:
        did = str(uuid.uuid4())
        return (
            f"https://service-stitcher.clusters.pluto.tv/stitch/hls/channel/{channel_id}/master.m3u8"
            f"?deviceId={did}&sid={did}&deviceType=web&deviceMake=Chrome"
            f"&deviceModel=Chrome&appName=web&appVersion=5.3.0"
            f"&clientID={client_id}&clientModelNumber=1&serverSideAds=true"
        )
    return None


async def get_pluto_stream_url(channel_id: str) -> str:
    channels = await fetch_pluto_channels()
    client_id = str(uuid.uuid4())
    if isinstance(channels, list):
        for ch in channels:
            if ch.get("_id") == channel_id:
                url = extract_stream_url(ch, client_id)
                if url:
                    return url
    did = str(uuid.uuid4())
    return (
        f"https://service-stitcher.clusters.pluto.tv/stitch/hls/channel/{channel_id}/master.m3u8"
        f"?deviceId={did}&sid={did}&deviceType=web&deviceMake=Chrome"
        f"&deviceModel=Chrome&appName=web&appVersion=5.3.0"
        f"&clientID={did}&clientModelNumber=1&serverSideAds=true"
    )


@router.post("/import")
async def import_pluto_channels(db: Session = Depends(get_db)):
    """Importa todos los canales de Pluto TV a la base de datos."""
    try:
        raw = await fetch_pluto_channels()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error conectando a Pluto TV: {str(e)}")

    channels_list = raw if isinstance(raw, list) else []

    cat = db.query(Category).filter(Category.slug == "pluto").first()
    if not cat:
        cat = Category(name="Pluto TV", slug="pluto", icon="fa-play-circle")
        db.add(cat)
        db.flush()

    client_id = str(uuid.uuid4())
    added = 0
    updated = 0

    for ch_data in channels_list:
        channel_id = ch_data.get("_id")
        name = ch_data.get("name") or ch_data.get("title")
        if not channel_id or not name:
            continue

        slug = f"pluto-{channel_id}"
        stream_url = f"pluto:{channel_id}"
        logo = None
        images = ch_data.get("images") or {}
        if isinstance(images, dict):
            logo = images.get("logo") or images.get("thumbnail")
        elif isinstance(images, list) and images:
            logo = images[0].get("url")

        existing = db.query(Channel).filter(Channel.slug == slug).first()
        if existing:
            existing.name = name
            existing.stream_url = stream_url
            if logo:
                existing.logo_url = logo
            existing.is_active = True
            updated += 1
        else:
            db.add(Channel(
                name=name,
                slug=slug,
                stream_url=stream_url,
                logo_url=logo,
                category_id=cat.id,
                is_active=True,
            ))
            added += 1

    db.commit()
    return {"imported": added, "updated": updated, "total_from_api": len(channels_list)}


@router.get("/channels")
async def list_pluto_channels():
    """Lista los canales disponibles en Pluto TV (sin importar a DB)."""
    try:
        raw = await fetch_pluto_channels()
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
    channels_list = raw if isinstance(raw, list) else []
    return [
        {"id": ch.get("_id"), "name": ch.get("name") or ch.get("title"),
         "category": ch.get("category")}
        for ch in channels_list if ch.get("_id")
    ]
