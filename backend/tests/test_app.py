import pytest

from politica import create_app
from politica.config import CHAVE_PADRAO, ProductionConfig


def test_producao_exige_secret_key_propria():
    class SemChave(ProductionConfig):
        SECRET_KEY = CHAVE_PADRAO

    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        create_app(SemChave)


def test_producao_aceita_secret_key_definida():
    class ComChave(ProductionConfig):
        SECRET_KEY = "valor-aleatorio-longo"
        SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

    assert create_app(ComChave).config["SECRET_KEY"] == "valor-aleatorio-longo"
