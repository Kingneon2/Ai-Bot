from urllib.parse import quote
import requests

HF_API_KEY = "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"

def generate_video_bytes(prompt: str) -> bytes:
    clean_prompt = prompt.replace("/video", "").replace("/image", "").strip()
    encoded = quote(clean_prompt)
    
    # Try direct free Pollinations motion/video stream first
    pollinations_url = f"https://image.pollinations.ai/prompt/{encoded}%20gif%20video%20animation?width=512&height=512&nologo=true"
    
    try:
        res = requests.get(pollinations_url, timeout=45)
        if res.status_code == 200:
            return res.content
    except Exception:
        pass

    # Fallback to HF standard inference
    hf_url = "https://api-inference.huggingface.co/models/prompthero/openjourney"
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
        
