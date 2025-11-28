import os
import httpx
import re
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

async def get_image_url(query: str) -> str:
    """
    Searches Pexels for an image. Falls back to placeholder if API fails.
    """
    # Fallback immediately if no key provided
    if not PEXELS_API_KEY or "your_pexels_key" in PEXELS_API_KEY:
        return f"[https://placehold.co/600x400?text=](https://placehold.co/600x400?text=){query.replace(' ', '+')}"

    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": 1, "orientation": "landscape"}
    url = "[https://api.pexels.com/v1/search](https://api.pexels.com/v1/search)"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params, timeout=5.0)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("photos"):
                    return data["photos"][0]["src"]["landscape"]
            else:
                logger.warning(f"Pexels API Error {response.status_code}: {response.text}")

    except Exception as e:
        logger.error(f"Failed to fetch image for '{query}': {e}")
    
    # Final fallback
    return f"[https://placehold.co/600x400?text=](https://placehold.co/600x400?text=){query.replace(' ', '+')}"

async def inject_images(html_content: str) -> str:
    """
    Replaces [IMAGE: query] tags with real URLs.
    """
    pattern = r"\[IMAGE:\s*(.*?)\]"
    matches = re.findall(pattern, html_content)
    
    if not matches:
        return html_content

    logger.info(f"Found image requests: {matches}")
    current_html = html_content
    
    # Use set() to process unique queries only
    for query in set(matches):
        image_url = await get_image_url(query)
        placeholder_tag = f"[IMAGE: {query}]"
        current_html = current_html.replace(placeholder_tag, image_url)
        
    return current_html