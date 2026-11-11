from datetime import date, timedelta

import pytest

from politica.errors import ErroServicoExterno
from politica.legislation import integracoes, services
from politica.legislation.models import Votacao

HOJE = date.today()


def votacao(id_, objeto, aprovacao, dias_atras=0, hora="15:30:00", descricao=None):
    dia = (HOJE - timedelta(days=dias_atras)).isoformat()
    return {
        "id": id_,
        "data": dia,
        "dataHoraRegistro": f"{dia}T{hora}",
        "proposicaoObjeto": objeto,
        "descricao": descricao or f"Votação de {objeto}",
        "aprovacao": aprovacao,
    }


@pytest.fixture
def camara(monkeypatch):
    chamadas = []
    dados = [
        votacao("1-1", "PL 10/2026", 1),
        votacao("1-2", "PEC 5/2026", 0, hora="16:00:00"),
        votacao("1-3", "PLP 3/2026", None, hora="17:00:00"),
        votacao("1-4", "REQ 99/2026", 1),
        votacao("1-5", None, 1, descricao="Aprovada a Redação Final."),
        votacao("1-9", "PL 40/2026", 1, descricao="Aprovado o requerimento nº 1/2026 que solicita urgência para o PL 40/2026."),
        votacao("1-10", "PL 41/2026", 1, descricao="Alteração do Regime de Tramitação desta proposição."),
        votacao("1-8", None, 1, hora="18:00:00", descricao="Aprovado o Substitutivo ao Projeto de Lei nº 464, de 2026."),
        votacao("1-6", "PL 20/2026", 1, dias_atras=3),
        votacao("1-7", "PL 30/2026", 1, dias_atras=15),
    ]

    def buscar(inicio, fim):
        chamadas.append((inicio, fim))
        return [v for v in dados if inicio.isoformat() <= v["data"] <= fim.isoformat()]

    monkeypatch.setattr(integracoes, "votacoes_do_periodo", buscar)
    return chamadas


def listar(client, **parametros):
    consulta = "&".join(f"{k}={v}" for k, v in parametros.items())
    return client.get(f"/api/legislation/votacoes?{consulta}")


def test_hoje_lista_so_projetos_de_lei_do_dia(client, camara):
    corpo = listar(client, periodo="hoje").json

    assert corpo["total"] == 4
    assert {v["objeto"] for v in corpo["itens"]} == {"PL 10/2026", "PEC 5/2026", "PLP 3/2026", None}


def test_ignora_votacoes_procedimentais(client, camara):
    objetos = {v["objeto"] for v in listar(client, periodo="hoje").json["itens"]}

    assert "PL 40/2026" not in objetos
    assert "PL 41/2026" not in objetos


def test_aceita_votacao_sem_objeto_quando_a_descricao_cita_projeto(client, camara):
    itens = listar(client, periodo="hoje").json["itens"]

    sem_objeto = [v for v in itens if v["objeto"] is None]
    assert [v["descricao"] for v in sem_objeto] == ["Aprovado o Substitutivo ao Projeto de Lei nº 464, de 2026."]


def test_periodo_padrao_e_hoje(client, camara):
    assert client.get("/api/legislation/votacoes").json["total"] == 4


def test_semana_e_mes_ampliam_o_intervalo(client, camara):
    assert listar(client, periodo="semana").json["total"] == 5
    assert listar(client, periodo="mes").json["total"] == 6


def test_status_e_traduzido(client, camara):
    itens = listar(client, periodo="hoje").json["itens"]

    status = {v["objeto"]: v["status"] for v in itens if v["objeto"]}
    assert status == {"PL 10/2026": "Aprovado", "PEC 5/2026": "Rejeitado", "PLP 3/2026": "Em andamento"}


def test_filtra_por_status(client, camara):
    for filtro, esperado in [("aprovado", 2), ("rejeitado", 1), ("andamento", 1)]:
        assert listar(client, periodo="hoje", status=filtro).json["total"] == esperado


def test_ordena_do_mais_recente_para_o_mais_antigo(client, camara):
    objetos = [v["objeto"] for v in listar(client, periodo="semana").json["itens"]]

    assert objetos == [None, "PLP 3/2026", "PEC 5/2026", "PL 10/2026", "PL 20/2026"]


def test_pagina_resultados(client, camara):
    corpo = listar(client, periodo="semana", por_pagina=3, pagina=2).json

    assert len(corpo["itens"]) == 2
    assert corpo["total_paginas"] == 2


def test_nao_consulta_a_camara_de_novo_dentro_do_intervalo(client, camara):
    listar(client, periodo="hoje")
    listar(client, periodo="hoje", status="aprovado")

    assert len(camara) == 1


def test_atualiza_votacao_existente_sem_duplicar(client, camara, monkeypatch):
    listar(client, periodo="hoje")
    assert Votacao.query.filter_by(id_original="1-3").one().aprovada is None

    services.sincronizacoes_votacoes.clear()
    monkeypatch.setattr(integracoes, "votacoes_do_periodo", lambda i, f: [votacao("1-3", "PLP 3/2026", 1)])
    listar(client, periodo="hoje")

    assert Votacao.query.filter_by(id_original="1-3").count() == 1
    assert Votacao.query.filter_by(id_original="1-3").one().status == "Aprovado"


def test_camara_fora_do_ar_sem_dados_retorna_502(client, monkeypatch):
    def falhar(inicio, fim):
        raise ErroServicoExterno("API da Câmara indisponível no momento.")

    monkeypatch.setattr(integracoes, "votacoes_do_periodo", falhar)

    assert listar(client, periodo="hoje").status_code == 502


def test_camara_fora_do_ar_serve_dados_ja_salvos(client, camara, monkeypatch):
    listar(client, periodo="hoje")

    def falhar(inicio, fim):
        raise ErroServicoExterno("API da Câmara indisponível no momento.")

    services.sincronizacoes_votacoes.clear()
    monkeypatch.setattr(integracoes, "votacoes_do_periodo", falhar)

    resposta = listar(client, periodo="hoje")

    assert resposta.status_code == 200
    assert resposta.json["total"] == 4


def test_valida_parametros(client):
    resposta = listar(client, periodo="ano", status="x", pagina=0)

    assert resposta.status_code == 422
    assert set(resposta.json["detalhes"]) == {"periodo", "status", "pagina"}
