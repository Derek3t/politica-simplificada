from politica.extensions import oauth

from . import models
from .routes import auth_bp

ESCOPOS_GOOGLE = "openid email profile https://www.googleapis.com/auth/calendar.events"


def init_app(app):
    oauth.register(
        name="google",
        client_id=app.config["GOOGLE_CLIENT_ID"],
        client_secret=app.config["GOOGLE_CLIENT_SECRET"],
        server_metadata_url=app.config["GOOGLE_METADATA_URL"],
        client_kwargs={"scope": ESCOPOS_GOOGLE},
    )
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
