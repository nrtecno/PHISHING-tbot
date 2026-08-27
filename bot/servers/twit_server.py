def register_twit_routes(app):
    @app.route('/p/twit/<uid>')
    def twit_page(uid):
        return "<h1>⏳ Twitter is coming soon!</h1>"
