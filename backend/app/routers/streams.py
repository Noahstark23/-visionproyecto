import re
import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from urllib.parse import quote, urljoin

from app.config import settings

router = APIRouter(prefix="/api/streams", tags=["streams"])

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://tvtvhd.com/",
}


async def get_stream_url(channel_slug: str) -> str:
    tvtvhd_url = f"https://tvtvhd.com/vivo/canales.php?stream={channel_slug}"

    async with httpx.AsyncClient(timeout=15, headers=HEADERS, follow_redirects=True) as client:
        response = await client.get(tvtvhd_url)
        html = response.text

    patterns = [
        r'playbackURL\s*[=:]\s*["\']?([^"\'<>\s]+\.m3u8[^"\'<>\s]*)',
        r'<source[^>]+src=["\']([^"\']+\.m3u8[^"\']*)',
        r'(https?://[^"\'<>\s]+\.m3u8[^"\'<>\s]*)',
    ]
    for pattern in patterns:
        match = re.search(pattern, html)
        if match:
            url = match.group(1)
            if url.startswith('http'):
                return url

    raise HTTPException(status_code=404, detail="Stream no encontrado")


def rewrite_playlist(content: str, base_url: str) -> str:
    proxy_base = f"{settings.BACKEND_URL}/api/streams"
    lines = []
    for line in content.split('\n'):
        stripped = line.strip()
        if stripped and not stripped.startswith('#'):
            seg_url = stripped if stripped.startswith('http') else urljoin(base_url, stripped)
            lines.append(f"{proxy_base}/segment?url={quote(seg_url, safe='')}")
        else:
            lines.append(line)
    return '\n'.join(lines)


@router.get("/segment")
async def proxy_segment(url: str):
    async with httpx.AsyncClient(headers=HEADERS, timeout=30, follow_redirects=True) as client:
        response = await client.get(url)

    content_type = response.headers.get('content-type', 'video/MP2T')

    if 'm3u8' in content_type or 'm3u8' in url.lower():
        base_url = url.split('?')[0].rsplit('/', 1)[0] + '/'
        content = rewrite_playlist(response.text, base_url)
        return Response(
            content=content,
            media_type='application/vnd.apple.mpegurl',
            headers={'Access-Control-Allow-Origin': '*', 'Cache-Control': 'no-cache'},
        )

    return Response(
        content=response.content,
        media_type=content_type,
        headers={'Access-Control-Allow-Origin': '*'},
    )


@router.get("/{channel_slug}/playlist.m3u8")
async def proxy_playlist(channel_slug: str):
    real_url = await get_stream_url(channel_slug)
    base_url = real_url.rsplit('/', 1)[0] + '/'

    async with httpx.AsyncClient(headers=HEADERS, timeout=15, follow_redirects=True) as client:
        response = await client.get(real_url)

    content = rewrite_playlist(response.text, base_url)
    return Response(
        content=content,
        media_type='application/vnd.apple.mpegurl',
        headers={'Access-Control-Allow-Origin': '*', 'Cache-Control': 'no-cache'},
    )


@router.get("/{channel_slug}")
async def get_stream(channel_slug: str):
    stream_url = await get_stream_url(channel_slug)
    return {"url": stream_url, "channel": channel_slug}
