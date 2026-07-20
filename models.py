import requests

GEMINI_API_KEY = "AQ.Ab8RN6KT9RQm0hYECEsL_S59o6PniTCc95kPBXvqEd13Le6R0w"
GROQ_API_KEY = "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"
OPENROUTER_API_KEY = "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"
MISTRAL_API_KEY = "6WuGmf9myQ15mB4sxDTzvJFcXrwXpFRV"
CEREBRAS_API_KEY = "csk-5hktwy3f2frttdwpkkjjc2dcmk5jedkxnjfw5r84v66xdwey"

def generate_text_response(prompt: str, user_state: dict) -> str:
    # Try Groq API
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
        except Exception:
            pass

    return f"Received: '{prompt}'"
    
