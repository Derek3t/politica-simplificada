from flask import Flask
from .config import Config
from .ext.db import init_app as init_db
from politica.auth import init_app as init_auth
from politica.legislation import init_app as init_legislation

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializa banco de dados
    init_db(app)
    init_auth(app)
    init_legislation(app)

    return app