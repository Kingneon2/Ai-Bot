"""
Routes a chat turn to whichever text model the user picked.

Every model below has a genuinely free tier. Groq, OpenRouter, Mistral,
Cerebras, and Hugging Face's router all speak the same OpenAI-style
chat-completions schema, so one function (`call_openai_compatible`)
handles all of them — only the base URL, key, and model name differ.
Gemini uses Google's own schema so it gets its own function.

IMPORTANT: put your actual key VALUES only in Render's Environment tab,
never in this file or in chat. Rotate any key that was ever pasted into
a chat window before using it here.
"""
import os
import requests

# ---- Provider config: (env var for key, base url, default model, display label) ----
PROVIDERS = {
    "groq": {
        "key_env": "GROQ_API_KEY",
        "base_url": "https://api.groq.com/openai/v1/chat/completions",
        "model_env": "GROQ_MODEL",
        "default_model": "llama-3.3-70b-versatile",
        "label": "⚡ Groq (Llama)",
    },
    "openrouter": {
        "key_env": "OPENROUTER_API_KEY",
        "base_url": "https://openrouter.ai/api/v1/chat/completions",
        "model_env": "OPENROUTER_MODEL",
        "default_model": "meta-llama/llama-3.1-8b-instruct:free",
        "label": "🌐 OpenRouter",
    },
    "mistral": {
        "key_env": "MISTRAL_API_KEY",
        "base_url": "https://api.mistral.ai/v1/chat/completions",
        "model_env": "MISTRAL_MODEL",
        "default_model": "mistral-small-latest",
        "label": "🌪️ Mistral",
    },
    "cerebras": {
        "key_env": "CEREBRAS_API_KEY",
        "base_url": "https://api.cerebras.ai/v1/chat/completions",
        "model_env": "CEREBRAS_MODEL",
        "default_model": "llama3.1-8b",
        "label": "🧠 Cerebras",
    },
    "huggingface": {
        "key_env": "HF_API_KEY",
        "base_url": "https://router.huggingface.co/v1/chat/completions",
        "model_env": "HF_MODEL",
        "default_model": "meta-llama/Llama-3.1-8B-Instruct",
        "label": "🤗 Hugging Face",
    },
}

GOOGLE_API_KEY = os.environ.get("GEMINI_API_KEY")
GOOGLE_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")  # optional
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5")


def available_models():
    """Only show models whose API key is actually configured."""
    choices = {}
    if GOOGLE_API_KEY:
        choices["gemini"] = "🔵 Gemini"
    if ANTHROPIC_API_KEY:
        choices["claude"] = "🟣 Claude"
    for key, cfg in PROVIDERS.items():
        if os.environ.get(cfg["key_env"]):
            choices[key] = cfg["label"]
    return choices


def call_openai_compatible(provider_key, history):
    cfg = PROVIDERS[provider_key]
    api_key = os.environ.get(cfg["key_env"])
    model = os.environ.get(cfg["model_env"], cfg["default_model"])
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body = {"model": model, "messages": history}
    r = requests.post(cfg["base_url"], headers=headers, json=body, timeout=60)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def call_gemini(history):
    contents = [
        {"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]}
        for m in history
    ]
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GOOGLE_MODEL}:generateContent?key={GOOGLE_API_KEY}"
    r = requests.post(url, json={"contents": contents}, timeout=60)
    r.raise_for_status()
    data = r.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


def call_claude(history, web_search=False):
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    body = {"model": CLAUDE_MODEL, "max_tokens": 1000, "messages": history}
    if web_search:
        body["tools"] = [{"type": "web_search_20250305", "name": "web_search"}]
    r = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=body, timeout=60)
    r.raise_for_status()
    data = r.json()
    return "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")


def ask(model_key, history, web_search=False):
    if model_key == "gemini":
        return call_gemini(history)
    if model_key == "claude":
        return call_claude(history, web_search=web_search)
    if model_key in PROVIDERS:
        return call_openai_compatible(model_key, history)
    # fallback to first available model
    fallback = next(iter(available_models()), None)
    if fallback is None:
        raise RuntimeError("No model API keys configured.")
    return ask(fallback, history, web_search=web_search)
