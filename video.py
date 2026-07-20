import requests

HF_API_KEY = "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"

def generate_video_bytes(prompt: str) -> bytes:
    # Uses Hugging Face inference provider router
    API_URL = "https://router.huggingface.co/hf-inference/models/damo-vilab/text-to-video-ms-1.7b"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    
    response = requests.post(
        API_URL, 
        headers=headers, 
        json={"inputs": prompt}, 
        timeout=60
    )
    
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"HF Error ({response.status_code}): {response.text}")
        
