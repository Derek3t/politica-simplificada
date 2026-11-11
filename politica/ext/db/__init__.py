from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine

db = SQLAlchemy()

def init_app(app):
    db.init_app(app)
    
    # Importa os models para o metadata registrar as tabelas
    with app.app_context():
        import politica.auth.models
        import politica.legislation.models

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()