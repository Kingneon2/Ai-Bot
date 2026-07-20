import os
import requests
from flask import Flask, request

import models
import images
import payments
import storage

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
# Numeric ID for private channels (e.g. -1001234567890), or "@username" for public ones.
CHANNEL_ID = os.environ["CHANNEL_ID"]
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

app = Flask(__name__)


def tg(method, **params):
    return requests.post(f"{TELEGRAM_API}/{method}", json=params, timeout=15).json()


def is_member(user_id: int) -> bool:
    res = tg("getChatMember", chat_id=CHANNEL_ID, user_id=user_id)
    if not res.get("ok"):
        return False
    return res["result"]["status"] in ("member", "administrator", "creator")


def send_join_prompt(chat_id):
    invite_url = os.environ.get("CHANNEL_INVITE_LINK", "https://t.me/")
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
        [{"text": "🔎 Web Search", "callback_data": "menu:search"},
         {"text": "🚀 Premium", "callback_data": "menu:premium"}],
    ]}


def model_menu_keyboard():
    choices = models.available_models()
    rows = [[{"text": label, "callback_data": f"setmodel:{key}"}] for key, label in choices.items()]
    rows.append([{"text": "Close", "callback_data": "menu:close"}])
    return {"inline_keyboard": rows}


def send_main_menu(chat_id):
    tg("sendMessage", chat_id=chat_id, text="What do you want to do?", reply_markup=main_menu_keyboard())


# ---------- Callback (button) handling ----------

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

    if not is_member(user_id):
        send_join_prompt(chat_id)
        return

    u = storage.get_user(chat_id)

    if data == "menu:close":
        tg("sendMessage", chat_id=chat_id, text="Closed.")
    elif data == "menu:model":
        tg("sendMessage", chat_id=chat_id, text="Pick a model:", reply_markup=model_menu_keyboard())
    elif data == "menu:image":
        u["mode"] = "image"
        tg("sendMessage", chat_id=chat_id, text="Image mode on. Send a prompt and I'll generate it.")
    elif data == "menu:search":
        u["mode"] = "search"
        tg("sendMessage", chat_id=chat_id, text="Web search mode on. Ask me anything current.")
    elif data == "menu:premium":
        tg("sendMessage", chat_id=chat_id, text="Go premium for unlimited chat + images:",
           reply_markup=payments.build_plans_keyboard())
    elif data.startswith("setmodel:"):
        key = data.split(":", 1)[1]
        u["model"] = key
        u["mode"] = "chat"
        label = models.available_models().get(key, key)
        tg("sendMessage", chat_id=chat_id, text=f"Model set to {label}.")
    elif data.startswith("buy:"):
        plan_key = data.split(":", 1)[1]
        invoice = payments.invoice_payload_for(plan_key)
        tg("sendInvoice", chat_id=chat_id, provider_token="", **invoice)


# ---------- Message handling ----------

def handle_text(chat_id, user_id, text):
    if not is_member(user_id):
        send_join_prompt(chat_id)
        return

    if text == "/start":
        send_main_menu(chat_id)
        return
    if text == "/menu":
        send_main_menu(chat_id)
        return

    u = storage.get_user(chat_id)

    if u["mode"] == "image":
        if not storage.can_generate_image(chat_id):
            tg("sendMessage", chat_id=chat_id, text="Free image limit reached today. /menu → Premium for more.")
            return
        tg("sendChatAction", chat_id=chat_id, action="upload_photo")
        try:
            url = images.generate_image_url(text)
            tg("sendPhoto", chat_id=chat_id, photo=url, caption=text[:200])
            storage.record_image(chat_id)
        except Exception as e:
            tg("sendMessage", chat_id=chat_id, text=f"Image generation failed: {e}")
        return

    # chat or search mode
    if not storage.can_send_message(chat_id):
        tg("sendMessage", chat_id=chat_id, text="Free daily message limit reached. /menu → Premium for more.")
        return

    tg("sendChatAction", chat_id=chat_id, action="typing")
    u["history"].append({"role": "user", "content": text})
    u["history"][:] = u["history"][-10:]

    try:
        reply = models.ask(u["model"], u["history"], web_search=(u["mode"] == "search"))
    except Exception as e:
        reply = f"Error: {e}"

    u["history"].append({"role": "assistant", "content": reply})
    storage.record_message(chat_id)
    tg("sendMessage", chat_id=chat_id, text=reply)


# ---------- Payments ----------

def handle_pre_checkout(pcq):
    tg("answerPreCheckoutQuery", pre_checkout_query_id=pcq["id"], ok=True)


def handle_successful_payment(msg):
    chat_id = msg["chat"]["id"]
    plan_key = msg["successful_payment"]["invoice_payload"]
    _, days, _ = payments.PLANS[plan_key]
    storage.grant_premium(chat_id, days)
    tg("sendMessage", chat_id=chat_id, text=f"Premium activated for {days} days. Enjoy 🚀")


# ---------- Webhook ----------

@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json(force=True)

    if "callback_query" in update:
        handle_callback(update["callback_query"])
        return "ok"

    if "pre_checkout_query" in update:
        handle_pre_checkout(update["pre_checkout_query"])
        return "ok"

    if "message" in update:
        msg = update["message"]
        if "successful_payment" in msg:
            handle_successful_payment(msg)
            return "ok"
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
