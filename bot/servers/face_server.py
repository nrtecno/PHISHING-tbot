def register_face_routes(app):
    @app.route('/p/face/<uid>')
    def face_page(uid):
        return "<h1>⏳ Facebook is coming soon!</h1>"
