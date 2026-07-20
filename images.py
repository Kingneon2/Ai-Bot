from urllib.parse import quote

POLLINATIONS_API_KEY = "sk_vJiGaquDZf8vSA6IEHAVhbMbChG3OR4z"

def generate_image_url(prompt: str) -> str:
    encoded = quote(prompt.strip())
    # Uses official gen.pollinations.ai unified endpoint
    url = f"https://gen.pollinations.ai/image/{encoded}?key={POLLINATIONS_API_KEY}&width=1024&height=1024"
    return url
    
