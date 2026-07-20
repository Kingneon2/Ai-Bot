import os
import requests

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

MODELS = {
    "llama-3.3-70b": "meta-llama/llama-3.3-70b-instruct",
    "llama-3.1-8b": "meta-llama/llama-3.1-8b-instant",
    "mixtral-8x7b": "mistralai/mixtral-8x7b-instruct",
    "gemma2-9b": "gemma2-9b-it"
}

def available_models():
    return {
        "llama-3.3-70b": "🧠 Llama 3.3 70B",
        "llama-3.1-8b": "⚡ Llama 3.1 8B (Fast)",
        "mixtral-8x7b": "🌀 Mixtral 8x7B",
        "gemma2-9b": "💎 Gemma 2 9B"
    }

def ask(model_key, history, web_search=False):
    model_id = MODELS.get(model_key, "meta-llama/llama-3.3-70b-instruct")
    
    if not GROQ_API_KEY:
        # Fallback if API key isn't in Render env variables yet
        return f"Groq API key missing. Last prompt: {history[-1]['content']}"

    try:
        res = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": model_id,
                "messages": history
            },
            timeout=15
        )
        if res.status_code == 200:
            return res.json()["choices"][0]["message"]["content"]
        else:
            return f"API Error ({res.status_code}): {res.text}"
    except Exception as e:
        return f"Request failed: {e}"
        
