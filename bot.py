import os
import requests

GROQ_API_KEY = "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"
OPENROUTER_API_KEY = "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"
CEREBRAS_API_KEY = "csk-5hktwy3f2frttdwpkkjjc2dcmk5jedkxnjfw5r84v66xdwey"
MISTRAL_API_KEY = "6WuGmf9myQ15mB4sxDTzvJFcXrwXpFRV"

def available_models():
    return {
        "groq-llama": "🧠 Llama 3.3 70B (Groq)",
        "cerebras-llama": "⚡ Llama 3.1 8B (Cerebras Ultra-Fast)",
        "openrouter-auto": "🌀 Auto Model (OpenRouter)",
        "mistral-small": "💎 Mistral Small (Mistral AI)"
    }

def ask(model_key, history, web_search=False):
    last_msg = history[-1]["content"] if history else "Hello"

    # Option 1: Groq
    if model_key == "groq-llama" or not model_key:
        try:
            res = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                json={"model": "llama-3.3-70b-versatile", "messages": history},
                timeout=15
            )
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"]
        except Exception:
            pass # Fall through to OpenRouter if Groq fails

    # Option 2: Cerebras (Ultra High Speed)
    if model_key == "cerebras-llama":
        try:
            res = requests.post(
                "https://api.cerebras.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {CEREBRAS_API_KEY}"},
                json={"model": "llama3.1-8b", "messages": history},
                timeout=15
            )
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"]
        except Exception:
            pass

    # Option 3: Mistral AI Direct
    if model_key == "mistral-small":
        try:
            res = requests.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {MISTRAL_API_KEY}"},
                json={"model": "mistral-small-latest", "messages": history},
                timeout=15
            )
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"]
        except Exception:
            pass

    # Universal Fallback: OpenRouter
    try:
        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://telegram.org",
            },
            json={"model": "meta-llama/llama-3.3-70b-instruct:free", "messages": history},
            timeout=15
        )
        if res.status_code == 200:
            return res.json()["choices"][0]["message"]["content"]
        else:
            return f"API Error ({res.status_code}): {res.text}"
    except Exception as e:
        return f"All AI Providers Failed: {e}"
        
