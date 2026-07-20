import os
import requests

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")

def generate_text_response(prompt: str, user_state: dict = None) -> str:
    if GROQ_API_KEY:
        try:
            res = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=10
            )
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error connecting to AI: {e}"

    return f"Received: {prompt}"

def ask(model_name, history, web_search=False):
    # Extracts the latest user message from history
    last_msg = history[-1]["content"] if history else "Hello"
    return generate_text_response(last_msg)

def available_models():
    return {
        "llama-3.3-70b": "Llama 3.3 70B (Default)",
    }
    
