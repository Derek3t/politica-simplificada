from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_app(app):
    db.init_app(app)
    
    # Importa os models para o metadata registrar as tabelas
    with app.app_context():
        import politica.auth.models
        import politica.legislation.models