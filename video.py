from urllib.parse import quote
import requests

def generate_video_bytes(prompt: str) -> bytes:
    """
    Generates moving AI video bytes via Pollinations video endpoint.
    """
    clean_prompt = prompt.replace("/video", "").replace("/image", "").strip()
    encoded = quote(clean_prompt)
    
    # Using 'veo' or 'wan-fast' from the official allowed models list
    url = f"https://gen.pollinations.ai/video/{encoded}?model=veo&width=512&height=512"
    
    response = requests.get(url, timeout=90)
    
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"Video API Error ({response.status_code}): {response.text}")
        
