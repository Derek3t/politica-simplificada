import sqlite3

from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine

db = SQLAlchemy()
migrate = Migrate()
cors = CORS()


@event.listens_for(Engine, "connect")
def ativar_foreign_keys(conexao, _registro):
    if isinstance(conexao, sqlite3.Connection):
        cursor = conexao.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
