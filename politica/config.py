import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "chave-secreta-politica")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///politica.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    DEBUG = True