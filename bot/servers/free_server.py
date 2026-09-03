def register_free_routes(app):
    @app.route('/p/free/<uid>')
    def free_page(uid):
        return "<h1>⏳ Free Fire coming soon!</h1>"
