import logging
import os

from flask import Flask

from .cli import registrar_comandos
from .config import CONFIGURACOES
from .errors import registrar_handlers
from .extensions import cors, db, migrate


def configurar_logging(app):
    logging.basicConfig(
        level=app.config["LOG_LEVEL"],
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def create_app(config_class=None):
    app = Flask(__name__)
    app.config.from_object(config_class or CONFIGURACOES[os.getenv("APP_ENV", "development")])

    configurar_logging(app)

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=True,
    )

    from politica.auth import init_app as init_auth
    from politica.calendar_sync import init_app as init_calendar
    from politica.legislation import init_app as init_legislation

    init_auth(app)
    init_legislation(app)
    init_calendar(app)

    registrar_handlers(app)
    registrar_comandos(app)

    return app
