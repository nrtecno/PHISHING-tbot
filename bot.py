import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import time
import os
from config import BOT_TOKEN

bot = telebot.TeleBot(BOT_TOKEN)

def get_bottom_buttons():
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        KeyboardButton("📸 Cam Hack"),
        KeyboardButton("📱 Social Media"),
        KeyboardButton("📧 Gmail"),
        KeyboardButton("🎮 Free Fire"),
        KeyboardButton("🔗 All Links")
    )
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    bot.send_message(
        user_id,
        "🔥 *Choose your weapon:*\n\n"
        "📸 Cam Hack (working)\n"
        "📱 Social Media (coming soon)\n"
        "📧 Gmail (coming soon)\n"
        "🎮 Free Fire (coming soon)\n"
        "🔗 All Links (coming soon)",
        reply_markup=get_bottom_buttons(),
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda message: True)
def route_buttons(message):
    text = message.text

    if text == "📸 Cam Hack":
        bot.send_message(message.chat.id, "✅ Cam Hack button pressed! (Working)")

    elif text in ["📱 Social Media", "📧 Gmail", "🎮 Free Fire", "🔗 All Links"]:
        bot.send_message(
            message.chat.id,
            f"⏳ *{text}* is coming soon. Only *Cam Hack* is working right now.",
            reply_markup=get_bottom_buttons(),
            parse_mode="Markdown"
        )

    else:
        bot.send_message(
            message.chat.id,
            "❌ Use the buttons below.",
            reply_markup=get_bottom_buttons()
        )

if __name__ == "__main__":
    print("🤖 Bot is running...")
    while True:
        try:
            bot.infinity_polling(timeout=60)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
