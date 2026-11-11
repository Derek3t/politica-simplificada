import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "troque-esta-chave")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///politica.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    CAMARA_BASE_URL = "https://dadosabertos.camara.leg.br/api/v2"
    BRASIL_API_URL = "https://brasilapi.com.br/api/feriados/v1"
    HTTP_TIMEOUT = int(os.getenv("HTTP_TIMEOUT", "15"))


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    TESTING = True
    SECRET_KEY = "chave-de-teste"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    GEMINI_API_KEY = ""
    LOG_LEVEL = "WARNING"


CONFIGURACOES = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
