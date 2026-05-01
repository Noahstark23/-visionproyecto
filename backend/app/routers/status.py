import httpx
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.channel import Channel

router = APIRouter(prefix="/api/status", tags=["status"])

STATUS_URL = "https://tvtvhd.com/status.json"


@router.post("/sync")
async def sync_status(db: Session = Depends(get_db)):
    """Sincroniza is_active de todos los canales con tvtvhd.com/status.json"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(STATUS_URL)
        data = response.json()
    except Exception as e:
        return {"error": f"No se pudo obtener status.json: {str(e)}"}

    # status.json puede ser lista o dict — normalizar a {slug: bool}
    active_map: dict[str, bool] = {}
    if isinstance(data, list):
        for item in data:
            slug = item.get("slug") or item.get("stream") or item.get("id")
            status = item.get("status") or item.get("active") or item.get("estado")
            if slug:
                active_map[slug] = str(status).lower() in ("true", "active", "activo", "1", "on")
    elif isinstance(data, dict):
        for key, val in data.items():
            if isinstance(val, bool):
                active_map[key] = val
            elif isinstance(val, dict):
                status = val.get("status") or val.get("active") or val.get("estado")
                active_map[key] = str(status).lower() in ("true", "active", "activo", "1", "on")

    updated = 0
    channels = db.query(Channel).all()
    for ch in channels:
        if ch.slug in active_map:
            new_status = active_map[ch.slug]
            if ch.is_active != new_status:
                ch.is_active = new_status
                updated += 1

    db.commit()
    return {
        "synced": len(active_map),
        "channels_in_db": len(channels),
        "updated": updated,
    }


@router.get("/")
async def get_status():
    """Retorna el status.json crudo de tvtvhd.com"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(STATUS_URL)
        return response.json()
    except Exception as e:
        return {"error": str(e)}
