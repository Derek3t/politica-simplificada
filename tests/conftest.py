import pytest

from politica import create_app
from politica.config import TestingConfig
from politica.extensions import db
from politica.legislation import services
from politica.legislation.models import Parlamentar


@pytest.fixture
def app():
    app = create_app(TestingConfig)
    services.sincronizacoes_votacoes.clear()
    services.cache_feriados.clear()
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def usuario_logado(client):
    client.post("/api/auth/registro", json={"nome": "Ana Lima", "email": "ana@exemplo.com", "senha": "senha1234"})
    return client


@pytest.fixture
def parlamentar(app):
    deputado = Parlamentar(id_original=100, nome="Maria Souza", partido="PT", estado="ES")
    db.session.add(deputado)
    db.session.commit()
    return deputado
