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


def test_sqlite_usa_wal_e_espera_o_banco_liberar(tmp_path):
    from sqlalchemy import create_engine, text

    motor = create_engine(f"sqlite:///{tmp_path / 'teste.db'}")
    with motor.connect() as conexao:
        assert conexao.execute(text("PRAGMA journal_mode")).scalar() == "wal"
        assert conexao.execute(text("PRAGMA busy_timeout")).scalar() == 30_000
        assert conexao.execute(text("PRAGMA foreign_keys")).scalar() == 1
