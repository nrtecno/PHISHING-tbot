import threading
from bot import app
from bot.__init__ import run_bot

if __name__ == "__main__":
    print("🤖 Cam Hack is working...")
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, debug=False)
