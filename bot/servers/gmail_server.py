def register_gmail_routes(app):
    @app.route('/p/gmail/<uid>')
    def gmail_page(uid):
        return "<h1>⏳ Gmail coming soon!</h1>"
