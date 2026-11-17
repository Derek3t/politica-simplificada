from datetime import date
from urllib.parse import parse_qs, urlparse

import pytest
import requests
from authlib.integrations.base_client.errors import OAuthError

from politica.auth.models import Usuario
from politica.extensions import db, oauth
from politica.legislation.models import Agenda, ProjetoLei

PERFIL = {"sub": "123", "email": "Bia@Exemplo.com", "email_verified": True, "name": "Bia Souza"}


@pytest.fixture
def google(app, monkeypatch):
    oauth.google.server_metadata = {
        "_loaded_at": 1,
        "issuer": "https://accounts.google.com",
        "authorization_endpoint": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_endpoint": "https://oauth2.googleapis.com/token",
    }
    retorno = {"token": {"userinfo": PERFIL, "refresh_token": "refresh-1"}}

    def autorizar():
        if isinstance(retorno["token"], Exception):
            raise retorno["token"]
        return retorno["token"]

    monkeypatch.setattr(oauth.google, "authorize_access_token", autorizar)
    return retorno


def test_login_redireciona_para_o_google_com_escopo_do_calendar(client, google):
    resposta = client.get("/api/auth/google/login")

    assert resposta.status_code == 302
    destino = urlparse(resposta.location)
    params = parse_qs(destino.query)
    assert destino.netloc == "accounts.google.com"
    assert params["client_id"] == ["id-de-teste"]
    assert "https://www.googleapis.com/auth/calendar.events" in params["scope"][0]
    assert params["access_type"] == ["offline"]


def test_login_sem_credenciais_retorna_503(app, client):
    app.config["GOOGLE_CLIENT_ID"] = ""

    assert client.get("/api/auth/google/login").status_code == 503


def test_callback_cria_usuario_e_abre_sessao(client, google):
    resposta = client.get("/api/auth/google/callback")

    assert resposta.status_code == 302
    assert resposta.location.endswith("/agenda")
    usuario = client.get("/api/auth/me").json["usuario"]
    assert usuario["email"] == "bia@exemplo.com"
    assert usuario["google_calendar"] is True
    assert db.session.scalar(db.select(Usuario)).senha_hash is None


def test_callback_vincula_conta_existente_pelo_email(client, google):
    client.post("/api/auth/registro", json={"nome": "Bia", "email": "bia@exemplo.com", "senha": "senha1234"})
    client.post("/api/auth/logout")

    client.get("/api/auth/google/callback")

    usuarios = db.session.scalars(db.select(Usuario)).all()
    assert len(usuarios) == 1
    assert usuarios[0].google_id == "123"
    assert usuarios[0].senha_hash is not None


def test_conta_so_google_nao_entra_com_senha(client, google):
    client.get("/api/auth/google/callback")
    client.post("/api/auth/logout")

    resposta = client.post("/api/auth/login", json={"email": "bia@exemplo.com", "senha": "qualquer123"})

    assert resposta.status_code == 401


def test_callback_com_erro_do_google_volta_para_o_login(client, google):
    google["token"] = OAuthError(error="access_denied")

    resposta = client.get("/api/auth/google/callback")

    assert resposta.location.endswith("/login?erro=google")
    assert client.get("/api/auth/me").status_code == 401


def test_callback_recusa_email_nao_verificado(client, google):
    google["token"] = {"userinfo": {**PERFIL, "email_verified": False}, "refresh_token": "x"}

    resposta = client.get("/api/auth/google/callback")

    assert resposta.location.endswith("/login?erro=google")
    assert db.session.scalar(db.select(Usuario)) is None


@pytest.fixture
def projeto(app):
    agenda = Agenda(data=date(2026, 11, 11))
    agenda.projetos_lei.append(ProjetoLei(codigo_pl="PL 1/2026", titulo="Ementa", resumo="Resumo simples"))
    db.session.add(agenda)
    db.session.commit()
    return agenda.projetos_lei[0]


class RespostaFalsa:
    def __init__(self, status=200, corpo=None):
        self.status_code = status
        self.ok = status < 400
        self.text = ""
        self._corpo = corpo or {}

    def json(self):
        return self._corpo


@pytest.fixture
def requisicoes(monkeypatch):
    chamadas = []
    respostas = {
        "https://oauth2.googleapis.com/token": RespostaFalsa(corpo={"access_token": "acesso-1"}),
        "https://www.googleapis.com/calendar/v3/calendars/primary/events": RespostaFalsa(
            201, {"htmlLink": "https://calendar.google.com/evento"}
        ),
    }

    def post(url, **kwargs):
        chamadas.append((url, kwargs))
        resposta = respostas[url]
        if isinstance(resposta, Exception):
            raise resposta
        return resposta

    monkeypatch.setattr(requests, "post", post)
    return chamadas, respostas


def test_adicionar_ao_google_cria_evento_de_dia_inteiro(client, google, projeto, requisicoes):
    chamadas, _ = requisicoes
    client.get("/api/auth/google/callback")

    resposta = client.post(f"/api/calendar/projetos/{projeto.id}/google")

    assert resposta.status_code == 201
    assert resposta.json["link"] == "https://calendar.google.com/evento"
    token, evento = chamadas
    assert token[1]["data"]["refresh_token"] == "refresh-1"
    assert evento[1]["headers"]["Authorization"] == "Bearer acesso-1"
    assert evento[1]["json"] == {
        "summary": "Votação PL 1/2026",
        "description": "Resumo simples",
        "start": {"date": "2026-11-11"},
        "end": {"date": "2026-11-12"},
    }


def test_adicionar_ao_google_exige_login(client, projeto):
    assert client.post(f"/api/calendar/projetos/{projeto.id}/google").status_code == 401


def test_adicionar_ao_google_exige_conta_google(usuario_logado, projeto):
    assert usuario_logado.post(f"/api/calendar/projetos/{projeto.id}/google").status_code == 403


def test_token_revogado_pede_novo_login(client, google, projeto, requisicoes):
    _, respostas = requisicoes
    respostas["https://oauth2.googleapis.com/token"] = RespostaFalsa(400)
    client.get("/api/auth/google/callback")

    resposta = client.post(f"/api/calendar/projetos/{projeto.id}/google")

    assert resposta.status_code == 403


def test_google_fora_do_ar_retorna_502(client, google, projeto, requisicoes):
    _, respostas = requisicoes
    respostas["https://www.googleapis.com/calendar/v3/calendars/primary/events"] = requests.ConnectionError()
    client.get("/api/auth/google/callback")

    assert client.post(f"/api/calendar/projetos/{projeto.id}/google").status_code == 502
