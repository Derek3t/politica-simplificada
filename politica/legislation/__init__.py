from .routes import legislation_bp

def init_app(app):
    app.register_blueprint(legislation_bp, url_prefix="/api/legislation")