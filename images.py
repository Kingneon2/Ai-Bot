from urllib.parse import quote
import requests

def generate_image_bytes(prompt: str) -> bytes:
    clean_prompt = prompt.replace("/image", "").replace("/video", "").strip()
    encoded = quote(clean_prompt)
    # Free public Pollinations endpoint (no key required)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&nologo=true"
    
    res = requests.get(url, timeout=30)
    if res.status_code == 200:
        return res.content
    else:
        raise Exception(f"Image API Error ({res.status_code}): {res.text}")

def generate_image_url(prompt: str) -> str:
    clean_prompt = prompt.replace("/image", "").replace("/video", "").strip()
    encoded = quote(clean_prompt)
    return f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&nologo=true"
    
