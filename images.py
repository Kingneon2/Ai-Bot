"""
Free image generation via Pollinations.ai — no billing surprises, unlike
Replicate. An API key raises your rate limit but isn't strictly required
for basic use.

Docs: https://gen.pollinations.ai/docs
"""
import os
from urllib.parse import quote

POLLINATIONS_API_KEY = os.environ.get("POLLINATIONS_API_KEY")  # optional


def generate_image_url(prompt: str) -> str:
    """
    Returns a direct image URL. Telegram's sendPhoto will fetch it —
    no need to download/upload ourselves.
    """
    encoded = quote(prompt)
    url = f"https://gen.pollinations.ai/image/{encoded}"
    if POLLINATIONS_API_KEY:
        url += f"?key={POLLINATIONS_API_KEY}"
    return url
