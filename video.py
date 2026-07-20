from urllib.parse import quote
import requests

def generate_video_bytes(prompt: str) -> bytes:
    clean_prompt = prompt.replace("/video", "").replace("/image", "").strip()
    encoded = quote(clean_prompt)
    
    # Public endpoint without authentication requirements
    url = f"https://image.pollinations.ai/prompt/{encoded}%20video%20animation?width=512&height=512&nologo=true"
    
    response = requests.get(url, timeout=60)
    
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"Video API Error ({response.status_code}): {response.text}")
        
