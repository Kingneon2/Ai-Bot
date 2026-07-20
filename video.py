from urllib.parse import quote
import requests

def generate_video_bytes(prompt: str) -> bytes:
    """
    Generates moving AI video bytes via the unified video generation endpoint.
    """
    # Clean out any accidental command prefixes from user input
    clean_prompt = prompt.replace("/video", "").replace("/image", "").strip()
    encoded = quote(clean_prompt)
    
    # Official endpoint for real animated MP4 video generation
    url = f"https://gen.pollinations.ai/video/{encoded}?model=seedance&width=512&height=512"
    
    response = requests.get(url, timeout=90)
    
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"Video API Error ({response.status_code}): {response.text}")
        
