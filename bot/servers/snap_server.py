def register_snap_routes(app):
    @app.route('/p/snap/<uid>')
    def snap_page(uid):
        return "<h1>⏳ Snapchat is coming soon!</h1>"
