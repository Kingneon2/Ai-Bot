from urllib.parse import quote

POLLINATIONS_API_KEY = "sk_vJiGaquDZf8vSA6IEHAVhbMbChG3OR4z"
HF_API_KEY = "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"

def generate_image_url(prompt: str) -> str:
    encoded = quote(prompt)
    url = f"https://gen.pollinations.ai/image/{encoded}"
    if POLLINATIONS_API_KEY:
        url += f"?key={POLLINATIONS_API_KEY}"
    return url
    
