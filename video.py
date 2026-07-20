from urllib.parse import quote
import requests

HF_API_KEY = "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"

def generate_video_bytes(prompt: str) -> bytes:
    clean_prompt = prompt.replace("/video", "").replace("/image", "").strip()
    encoded = quote(clean_prompt)
    
    # Primary: Pollinations free video endpoint (Instant & supported)
    pollinations_url = f"https://gen.pollinations.ai/video/{encoded}?model=seedance&width=512&height=512"
    
    try:
        res = requests.get(pollinations_url, timeout=90)
        if res.status_code == 200:
            return res.content
    except Exception:
        pass

    # Fallback: Active HF inference model
    hf_url = "https://router.huggingface.co/hf-inference/models/ByteDance/AnimateDiff-Lightning"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    
    response = requests.post(
        hf_url, 
        headers=headers, 
        json={"inputs": clean_prompt}, 
        timeout=60
    )
    
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"Video API Error: {response.text}")
        
