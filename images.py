from urllib.parse import quote
import requests

POLLINATIONS_API_KEY = "sk_vJiGaquDZf8vSA6IEHAVhbMbChG3OR4z"

def generate_image_bytes(prompt: str) -> bytes:
    clean_prompt = prompt.replace("/image", "").replace("/video", "").strip()
    encoded = quote(clean_prompt)
    url = f"https://gen.pollinations.ai/image/{encoded}?key={POLLINATIONS_API_KEY}&width=1024&height=1024"
    
    # Downloads raw image bytes directly
    res = requests.get(url, timeout=30)
    if res.status_code == 200:
        return res.content
    else:
        raise Exception(f"Image API Error ({res.status_code}): {res.text}")
        
