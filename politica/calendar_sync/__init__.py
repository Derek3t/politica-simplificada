from .routes import calendar_bp

def init_app(app):
    app.register_blueprint(calendar_bp, url_prefix="/api/calendar")