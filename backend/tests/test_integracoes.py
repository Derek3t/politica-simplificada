import pytest
import requests

from politica.errors import ErroServicoExterno
from politica.legislation import integracoes


class RespostaFalsa:
    def __init__(self, corpo=None, status=200):
        self.corpo = corpo
        self.status = status

    def raise_for_status(self):
        if self.status >= 400:
            raise requests.HTTPError(f"status {self.status}")

    def json(self):
        if self.corpo is None:
            raise ValueError("sem JSON")
        return self.corpo


@pytest.fixture
def pausas(monkeypatch):
    registradas = []
    monkeypatch.setattr(integracoes.time, "sleep", registradas.append)
    return registradas


def simular(monkeypatch, respostas):
    chamadas = []

    def get(url, params=None, timeout=None, headers=None):
        chamadas.append(url)
        resposta = respostas[len(chamadas) - 1]
        if isinstance(resposta, Exception):
            raise resposta
        return resposta

    monkeypatch.setattr(integracoes.requests, "get", get)
    return chamadas


def buscar():
    return integracoes._buscar_json("https://exemplo.com/api", None, 5, "API de teste")


def test_sucesso_na_primeira_tentativa_nao_espera(monkeypatch, pausas):
    chamadas = simular(monkeypatch, [RespostaFalsa({"dados": [1]})])

    assert buscar() == {"dados": [1]}
    assert len(chamadas) == 1
    assert pausas == []


def test_tenta_de_novo_depois_de_timeout_e_erro_de_servidor(monkeypatch, pausas):
    chamadas = simular(monkeypatch, [requests.Timeout("lento"), RespostaFalsa(status=503), RespostaFalsa({"ok": True})])

    assert buscar() == {"ok": True}
    assert len(chamadas) == 3
    assert pausas == [0.5, 1.0]


def test_desiste_depois_de_todas_as_tentativas(monkeypatch, pausas):
    chamadas = simular(monkeypatch, [requests.ConnectionError("fora")] * 3)

    with pytest.raises(ErroServicoExterno, match="API de teste indisponível"):
        buscar()

    assert len(chamadas) == integracoes.TENTATIVAS
    assert len(pausas) == integracoes.TENTATIVAS - 1


def test_resposta_que_nao_e_json_tambem_conta_como_falha(monkeypatch, pausas):
    simular(monkeypatch, [RespostaFalsa(None)] * 3)

    with pytest.raises(ErroServicoExterno):
        buscar()
