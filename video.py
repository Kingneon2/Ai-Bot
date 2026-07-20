import os
import requests

HF_API_KEY = "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"

def generate_video_bytes(prompt: str) -> bytes:
    """
    Calls Hugging Face serverless inference to generate video bytes.
    """
    API_URL = "https://api-inference.huggingface.co/models/damo-vilab/text-to-video-ms-1.7b"
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
      
