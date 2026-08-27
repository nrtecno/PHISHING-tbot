from flask import Flask, request, jsonify
import time
import threading
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bot is running!"

@app.route('/p/<uid>')
def phishing_page(uid):
    return "Phishing page here"

@app.route('/api/capture', methods=['POST'])
def capture():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
