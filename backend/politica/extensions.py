import contextlib
import sqlite3

from authlib.integrations.flask_client import OAuth
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine

db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
oauth = OAuth()


ESPERA_DO_BANCO_MS = 30_000


@event.listens_for(Engine, "connect")
def configurar_sqlite(conexao, _registro):
    if isinstance(conexao, sqlite3.Connection):
        cursor = conexao.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        # a espera vem primeiro: até a troca para WAL precisa dela se outro processo estiver escrevendo
        cursor.execute(f"PRAGMA busy_timeout={ESPERA_DO_BANCO_MS}")
        # WAL deixa leituras e escrita andarem juntas. O modo fica gravado no arquivo; se outro processo estiver
        # escrevendo agora, a troca é adiada para a próxima conexão em vez de derrubar a requisição
        with contextlib.suppress(sqlite3.OperationalError):
            cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()
