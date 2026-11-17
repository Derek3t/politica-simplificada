from datetime import date

import pytest

from politica.errors import ErroServicoExterno
from politica.legislation import integracoes, services
from politica.legislation.models import Parlamentar, Votacao

HOJE = date.today()

SENADORES = [
    {"id": 1, "nome": "Senador Um", "siglaPartido": "MDB", "siglaUf": "AC", "urlFoto": "http://foto/1"},
    {"id": 2, "nome": "Senadora Dois", "siglaPartido": "PSB", "siglaUf": "MA", "urlFoto": None},
    {"id": 3, "nome": "Senador Três", "siglaPartido": "PP", "siglaUf": "SC", "urlFoto": None},
]


def votacao_senado(codigo, sigla="PEC", resultado="A", votos=None):
    return {
        "codigoSessaoVotacao": codigo,
        "dataSessao": HOJE.isoformat(),
        "identificacao": f"{sigla} 18/2025",
        "descricaoVotacao": f"Votação nominal da {sigla}",
        "sigla": sigla,
        "resultadoVotacao": resultado,
        "votos": votos
        if votos is not None
        else [
            {"codigoParlamentar": 1, "siglaVotoParlamentar": "Sim"},
            {"codigoParlamentar": 2, "siglaVotoParlamentar": "P-NRV"},
            {"codigoParlamentar": 777, "siglaVotoParlamentar": "Não"},
            {"codigoParlamentar": 3, "siglaVotoParlamentar": None, "descricaoVotoParlamentar": None},
        ],
    }


@pytest.fixture
def senado(monkeypatch):
    monkeypatch.setattr(integracoes, "listar_senadores", lambda: SENADORES)
    monkeypatch.setattr(integracoes, "votacoes_do_periodo", lambda inicio, fim: [])
    dados = [votacao_senado(10), votacao_senado(11, resultado="R"), votacao_senado(12, sigla="MSF")]
    monkeypatch.setattr(integracoes, "votacoes_senado", lambda inicio, fim: dados)
    return dados


def test_importa_senadores_sem_misturar_com_deputados(app, senado):
    from politica.extensions import db

    db.session.add(Parlamentar(id_original=1, nome="Deputado Um", partido="PT", estado="ES"))
    db.session.commit()

    assert services.importar_senadores() == (3, 0)
    assert services.importar_senadores() == (0, 3)
    assert Parlamentar.query.filter_by(casa="Senado").count() == 3
    assert Parlamentar.query.filter_by(casa="Câmara").count() == 1


def test_listagem_de_parlamentares_filtra_por_casa(client, app, senado):
    services.importar_senadores()

    assert client.get("/api/legislation/parlamentares?casa=Senado").json["total"] == 3
    assert client.get("/api/legislation/parlamentares?casa=C%C3%A2mara").json["total"] == 0
    assert client.get("/api/legislation/parlamentares?casa=Outra").status_code == 422


def test_votacoes_do_senado_entram_na_lista_com_os_votos(client, app, senado):
    services.importar_senadores()

    corpo = client.get("/api/legislation/votacoes?casa=Senado").json

    assert corpo["total"] == 2
    assert {v["casa"] for v in corpo["itens"]} == {"Senado"}
    assert {v["status"] for v in corpo["itens"]} == {"Aprovado", "Rejeitado"}
    detalhe = client.get(f"/api/legislation/votacoes/{corpo['itens'][0]['id']}").json
    assert detalhe["placar"] == {"Sim": 1, "Presente, sem voto": 1, "Sem registro": 1}


def test_so_projetos_do_senado_sao_considerados(client, app, senado):
    client.get("/api/legislation/votacoes?casa=Senado")

    assert Votacao.query.filter_by(casa="Senado").count() == 2


def test_senado_fora_do_ar_nao_derruba_a_lista(client, app, monkeypatch):
    monkeypatch.setattr(integracoes, "votacoes_do_periodo", lambda inicio, fim: [])

    def falhar(inicio, fim):
        raise ErroServicoExterno("fora do ar")

    monkeypatch.setattr(integracoes, "votacoes_senado", falhar)

    assert client.get("/api/legislation/votacoes").status_code == 200
