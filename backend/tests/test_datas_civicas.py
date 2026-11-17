from datetime import date

import pytest

from politica.extensions import db
from politica.legislation import integracoes
from politica.legislation.datas_civicas import (
    DATAS_CIVICAS,
    FERIADOS_ESTADUAIS,
    FERIADOS_NACIONAIS,
    contexto_do_feriado,
    dias_especiais_extras,
    normalizar,
)
from politica.legislation.models import Agenda, DiaEspecial

CAMPOS = {"contexto_historico", "importancia", "impacto_legislativo"}


def test_todo_texto_curado_tem_os_tres_campos_preenchidos():
    textos = list(FERIADOS_NACIONAIS.values()) + list(DATAS_CIVICAS.values())
    textos += [feriado for estado in FERIADOS_ESTADUAIS.values() for feriado in estado.values()]

    assert all(set(t) >= CAMPOS and all(t[c] for c in CAMPOS) for t in textos)


def test_datas_estaduais_sao_dias_validos():
    for uf, feriados in FERIADOS_ESTADUAIS.items():
        assert len(uf) == 2
        for mes, dia in feriados:
            date(2026, mes, dia)


@pytest.mark.parametrize(
    "nome",
    ["Confraternização mundial", "Dia do trabalho", "Independência do Brasil", "Dia da consciência negra", "Páscoa"],
)
def test_feriados_da_brasilapi_tem_contexto(nome):
    assert contexto_do_feriado(nome)["contexto_historico"]


def test_nome_sem_contexto_curado_retorna_none():
    assert contexto_do_feriado("Feriado Inventado") is None
    assert normalizar("  Páscoa ") == "pascoa"


def test_extras_trazem_data_civica_e_estadual_do_uf():
    nomes = [e["nome"] for e in dias_especiais_extras(date(2026, 10, 5), "to")]

    assert nomes == ["Promulgação da Constituição de 1988", "Criação do Estado do Tocantins"]


def test_extras_sem_uf_nao_trazem_feriado_estadual():
    assert [e["tipo"] for e in dias_especiais_extras(date(2026, 10, 5))] == ["civica"]
    assert dias_especiais_extras(date(2026, 7, 9)) == []
    assert dias_especiais_extras(date(2026, 7, 9), "SP")[0]["id"] is None


@pytest.fixture
def agenda(app, monkeypatch):
    monkeypatch.setattr(integracoes, "feriados_do_ano", lambda ano: [])
    monkeypatch.setattr(integracoes, "eventos_do_dia", lambda data: [])
    monkeypatch.setattr(integracoes, "pautas_dos_eventos", lambda ids: [])
    dados = Agenda(data=date(2026, 9, 7))
    dados.dias_especiais.append(DiaEspecial(nome="Independência do Brasil", tipo="national"))
    db.session.add(dados)
    db.session.commit()


def test_feriado_nacional_ja_salvo_ganha_contexto_sem_ia(client, agenda):
    corpo = client.get("/api/legislation/agenda?data=2026-09-07").json

    dia = corpo["dias_especiais"][0]
    assert "Grito do Ipiranga" in dia["contexto_historico"]
    assert dia["impacto_legislativo"]


def test_agenda_acrescenta_feriado_estadual_do_uf_informado(client, app, monkeypatch):
    monkeypatch.setattr(integracoes, "feriados_do_ano", lambda ano: [])
    monkeypatch.setattr(integracoes, "eventos_do_dia", lambda data: [])
    monkeypatch.setattr(integracoes, "pautas_dos_eventos", lambda ids: [])

    com_uf = client.get("/api/legislation/agenda?data=2026-07-09&uf=sp").json
    sem_uf = client.get("/api/legislation/agenda?data=2026-07-09").json

    assert [d["nome"] for d in com_uf["dias_especiais"]] == ["Revolução Constitucionalista de 1932"]
    assert com_uf["dias_especiais"][0]["tipo"] == "estadual"
    assert sem_uf["dias_especiais"] == []


def test_calendario_inclui_feriado_estadual_so_para_o_uf(client, monkeypatch):
    monkeypatch.setattr(integracoes, "feriados_do_ano", lambda ano: [])
    monkeypatch.setattr(integracoes, "votacoes_do_periodo", lambda inicio, fim: [])

    com_uf = client.get("/api/legislation/calendario?mes=2026-07&uf=BA").json
    sem_uf = client.get("/api/legislation/calendario?mes=2026-07").json

    assert com_uf["dias"]["2026-07-02"]["feriados"] == ["Independência da Bahia"]
    assert "2026-07-02" not in sem_uf["dias"]


def test_uf_invalido_retorna_422(client):
    assert client.get("/api/legislation/agenda?data=2026-07-09&uf=XYZ").status_code == 422


def test_contextualizar_feriado_com_texto_curado_nao_precisa_de_ia(usuario_logado, agenda):
    dia = DiaEspecial.query.one()

    resposta = usuario_logado.post(f"/api/legislation/dias-especiais/{dia.id}/contextualizar")

    assert resposta.status_code == 200
    assert "Grito do Ipiranga" in resposta.json["contexto_historico"]


def test_santa_catarina_tem_o_dia_do_estado():
    extras = dias_especiais_extras(date(2026, 8, 11), "SC")

    assert [(e["tipo"], e["nome"]) for e in extras][-1] == ("estadual", "Dia do Estado de Santa Catarina")
