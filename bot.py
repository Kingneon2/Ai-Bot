import os
import requests
from flask import Flask, request

import models
import images
import storage
import video

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8889911470:AAElM2itSzfhwmQAQO75gDIrnHfKHGgHxH0")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "-1003861121732")
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

app = Flask(__name__)


def tg(method, **params):
    try:
        res = requests.post(f"{TELEGRAM_API}/{method}", json=params, timeout=15)
        return res.json()
    except Exception as e:
        print(f"Telegram API Error ({method}): {e}")
        return {"ok": False}


def is_member(user_id: int) -> bool:
    if not CHANNEL_ID:
        return True
    res = tg("getChatMember", chat_id=CHANNEL_ID, user_id=user_id)
    if not res.get("ok"):
        return True
    return res.get("result", {}).get("status") in ("member", "administrator", "creator")


def send_join_prompt(chat_id):
    invite_url = os.environ.get("CHANNEL_INVITE_LINK", "https://t.me/+ckfO94UHyhllODg0")
    tg("sendMessage", chat_id=chat_id, text="Join the channel to use this bot.",
       reply_markup={"inline_keyboard": [
           [{"text": "📢 Join Channel", "url": invite_url}],
           [{"text": "✅ I've Joined", "callback_data": "recheck"}],
       ]})


# ---------- Menus ----------

def main_menu_keyboard():
    return {"inline_keyboard": [
        [{"text": "🧠 Choose Model", "callback_data": "menu:model"},
         {"text": "🎨 Image Generation", "callback_data": "menu:image"}],
        [{"text": "🎬 Video Generation", "callback_data": "menu:video"},
         {"text": "🔎 Web Search", "callback_data": "menu:search"}],
    ]}


def model_menu_keyboard():
    choices = models.available_models() if hasattr(models, 'available_models') else {"default": "Default AI"}
    rows = [[{"text": label, "callback_data": f"setmodel:{key}"}] for key, label in choices.items()]
    rows.append([{"text": "Close", "callback_data": "menu:close"}])
    return {"inline_keyboard": rows}


def send_main_menu(chat_id):
    tg("sendMessage", chat_id=chat_id, text="What do you want to do?", reply_markup=main_menu_keyboard())


# ---------- Callback handling ----------

def handle_callback(cq):
    user_id = cq["from"]["id"]
    chat_id = cq["message"]["chat"]["id"]
    data = cq["data"]
    tg("answerCallbackQuery", callback_query_id=cq["id"])

    if data == "recheck":
        if is_member(user_id):
            tg("sendMessage", chat_id=chat_id, text="You're verified! Send me anything.")
        else:
            tg("sendMessage", chat_id=chat_id, text="Still not in the channel. Join, then tap again.")
        return

    u = storage.get_user(chat_id)

    if data == "menu:close":
        tg("sendMessage", chat_id=chat_id, text="Closed.")
    elif data == "menu:model":
        tg("sendMessage", chat_id=chat_id, text="Pick a model:", reply_markup=model_menu_keyboard())
    elif data == "menu:image":
        u["mode"] = "image"
        tg("sendMessage", chat_id=chat_id, text="Image mode on. Send a prompt (e.g. 'A futuristic car')!")
    elif data == "menu:video":
        u["mode"] = "video"
        tg("sendMessage", chat_id=chat_id, text="Video mode on. Send a prompt (e.g. 'A running dog')!")
    elif data == "menu:search":
        u["mode"] = "search"
        tg("sendMessage", chat_id=chat_id, text="Web search mode on. Ask me anything current.")
    elif data.startswith("setmodel:"):
        key = data.split(":", 1)[1]
        u["model"] = key
        u["mode"] = "chat"
        choices = models.available_models() if hasattr(models, 'available_models') else {}
        label = choices.get(key, key)
        tg("sendMessage", chat_id=chat_id, text=f"Model set to {label}.")


# ---------- Message handling ----------

def handle_text(chat_id, user_id, text):
    if text in ("/start", "/menu"):
        send_main_menu(chat_id)
        return

    if not is_member(user_id):
        send_join_prompt(chat_id)
        return

    u = storage.get_user(chat_id)

    # 1. Image Mode
    if u.get("mode") == "image":
        tg("sendChatAction", chat_id=chat_id, action="upload_photo")
        try:
            # Uses generate_image_bytes if available, falls back to URL
            if hasattr(images, 'generate_image_bytes'):
                img_data = images.generate_image_bytes(text)
                requests.post(
                    f"{TELEGRAM_API}/sendPhoto",
                    data={"chat_id": chat_id, "caption": text[:200]},
                    files={"photo": ("image.jpg", img_data, "image/jpeg")}
                )
            else:
                url = images.generate_image_url(text)
                tg("sendPhoto", chat_id=chat_id, photo=url, caption=text[:200])
            storage.record_image(chat_id)
        except Exception as e:
            tg("sendMessage", chat_id=chat_id, text=f"Image generation failed: {e}")
        return

    # 2. Video Mode
    if u.get("mode") == "video":
        tg("sendChatAction", chat_id=chat_id, action="upload_video")
        try:
            video_data = video.generate_video_bytes(text)
            requests.post(
                f"{TELEGRAM_API}/sendVideo",
                data={"chat_id": chat_id, "caption": text[:200]},
                files={"video": ("generated.mp4", video_data, "video/mp4")}
            )
            storage.record_image(chat_id)
        except Exception as e:
            tg("sendMessage", chat_id=chat_id, text=f"Video generation failed: {e}")
        return

    # 3. Chat / Search Mode
    tg("sendChatAction", chat_id=chat_id, action="typing")
    u["history"].append({"role": "user", "content": text})
    u["history"][:] = u["history"][-10:]

    try:
        if hasattr(models, 'ask'):
            reply = models.ask(u.get("model", "groq-llama"), u["history"], web_search=(u.get("mode") == "search"))
        else:
            reply = models.generate_text_response(text, u)
    except Exception as e:
        reply = f"Error: {e}"

    u["history"].append({"role": "assistant", "content": reply})
    storage.record_message(chat_id)
    tg("sendMessage", chat_id=chat_id, text=reply)


# ---------- Webhook ----------

@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json(force=True)

    if "callback_query" in update:
        handle_callback(update["callback_query"])
        return "ok"

    if "message" in update:
        msg = update["message"]
        if "text" in msg:
            handle_text(msg["chat"]["id"], msg["from"]["id"], msg["text"])
        return "ok"

    return "ok"


@app.route("/", methods=["GET"])
def health():
    return "Bot is running."


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    
