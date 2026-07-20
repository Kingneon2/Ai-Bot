"""
Simple in-memory user store.
Resets on every redeploy — swap this for Redis or Postgres once you have
real traffic and want persistence. Keeping it in-memory keeps the demo
dependency-free.
"""
from datetime import date

FREE_DAILY_MESSAGES = 15
FREE_DAILY_IMAGES = 1

_users = {}


def get_user(chat_id):
    u = _users.setdefault(chat_id, {
        "model": None,  # set on first message from whichever provider is configured
        "mode": "chat",          # chat | image | search
        "premium_until": None,   # ISO date string or None
        "msg_count": 0,
        "img_count": 0,
        "count_date": str(date.today()),
        "history": [],
    })
    _reset_if_new_day(u)
    return u


def _reset_if_new_day(u):
    today = str(date.today())
    if u["count_date"] != today:
        u["count_date"] = today
        u["msg_count"] = 0
        u["img_count"] = 0


def is_premium(u):
    if not u["premium_until"]:
        return False
    return date.fromisoformat(u["premium_until"]) >= date.today()


def grant_premium(chat_id, days):
    from datetime import timedelta
    u = get_user(chat_id)
    start = date.today()
    if u["premium_until"] and date.fromisoformat(u["premium_until"]) > start:
        start = date.fromisoformat(u["premium_until"])
    u["premium_until"] = str(start + timedelta(days=days))


def can_send_message(chat_id):
    u = get_user(chat_id)
    return is_premium(u) or u["msg_count"] < FREE_DAILY_MESSAGES


def can_generate_image(chat_id):
    u = get_user(chat_id)
    return is_premium(u) or u["img_count"] < FREE_DAILY_IMAGES


def record_message(chat_id):
    get_user(chat_id)["msg_count"] += 1


def record_image(chat_id):
    get_user(chat_id)["img_count"] += 1
