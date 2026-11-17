import os

from dotenv import load_dotenv

load_dotenv()


CHAVE_PADRAO = "troque-esta-chave"


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", CHAVE_PADRAO)
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///politica.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b")
    CAMARA_BASE_URL = "https://dadosabertos.camara.leg.br/api/v2"
    SENADO_BASE_URL = "https://legis.senado.leg.br/dadosabertos"
    BRASIL_API_URL = "https://brasilapi.com.br/api/feriados/v1"
    HTTP_TIMEOUT = int(os.getenv("HTTP_TIMEOUT", "15"))
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:5173/api/auth/google/callback")
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
    GOOGLE_METADATA_URL = "https://accounts.google.com/.well-known/openid-configuration"
    GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_CALENDAR_URL = "https://www.googleapis.com/calendar/v3/calendars/primary/events"


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    TESTING = True
    SECRET_KEY = "chave-de-teste"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    OPENROUTER_API_KEY = ""
    GOOGLE_CLIENT_ID = "id-de-teste"
    GOOGLE_CLIENT_SECRET = "segredo-de-teste"
    LOG_LEVEL = "WARNING"


CONFIGURACOES = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
