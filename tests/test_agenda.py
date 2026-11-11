from datetime import date, timedelta

import pytest

from politica.errors import ErroServicoExterno
from politica.legislation import integracoes
from politica.legislation.models import Agenda, ProjetoLei

DATA = "2026-11-11"

EVENTOS = [
    {"id": 1, "descricaoTipo": "Sessão Deliberativa", "situacao": "Convocada", "dataHoraInicio": "2026-11-11T09:00", "orgaos": [{"nome": "Plenário", "sigla": "PLEN"}]},
    {"id": 2, "descricaoTipo": "Audiência Pública", "situacao": "Convocada", "orgaos": [{"nome": "CCJ"}]},
    {"id": 3, "descricaoTipo": "Reunião Deliberativa", "situacao": "Cancelada", "orgaos": [{"nome": "CFT"}]},
]

PAUTA = [
    {
        "titulo": "REQ 10/2026",
        "proposicao_": {"id": 11, "siglaTipo": "REQ", "numero": 10, "ano": 2026, "ementa": "Requer urgência."},
        "proposicaoRelacionada_": {"id": 22, "siglaTipo": "PL", "numero": "479", "ano": "2025", "ementa": "Define TDAH."},
    },
    {"titulo": "PEC 5/2026", "proposicao_": {"id": 33, "siglaTipo": "PEC", "numero": 5, "ano": 2026, "ementa": "Altera a Constituição."}},
    {"titulo": "TVR 9/2026", "proposicao_": {"id": 44, "siglaTipo": "TVR", "numero": 9, "ano": 2026, "ementa": "Concessão de rádio."}},
    {"titulo": "sem proposicao"},
]


@pytest.fixture
def camara(monkeypatch):
    chamadas = {"eventos": 0}

    def eventos(data):
        chamadas["eventos"] += 1
        return EVENTOS

    monkeypatch.setattr(integracoes, "eventos_do_dia", eventos)
    monkeypatch.setattr(integracoes, "pautas_dos_eventos", lambda ids: [PAUTA for _ in ids])
    monkeypatch.setattr(integracoes, "autores_das_proposicoes", lambda ids: {i: [100] if i == 22 else [] for i in ids})
    monkeypatch.setattr(
        integracoes,
        "feriados_do_ano",
        lambda ano: [{"date": DATA, "name": "Dia Teste", "type": "national"}, {"date": "2026-12-25", "name": "Natal"}],
    )
    return chamadas


def test_agenda_exige_data(client):
    resposta = client.get("/api/legislation/agenda")

    assert resposta.status_code == 422
    assert "data" in resposta.json["detalhes"]


def test_agenda_rejeita_data_invalida(client):
    assert client.get("/api/legislation/agenda?data=11-11-2026").status_code == 422


def test_agenda_monta_projetos_e_dias_especiais(client, camara):
    corpo = client.get(f"/api/legislation/agenda?data={DATA}&incluir_comissoes=true").json

    assert [p["codigo_pl"] for p in corpo["projetos_lei"]] == ["PL 479/2025", "PEC 5/2026"]
    assert corpo["projetos_lei"][0]["horario"] == "09:00"
    assert corpo["projetos_lei"][0]["orgao"] == "Plenário"
    assert [d["nome"] for d in corpo["dias_especiais"]] == ["Dia Teste"]


def test_agenda_mostra_so_plenario_por_padrao(client, camara):
    corpo = client.get(f"/api/legislation/agenda?data={DATA}").json

    assert {p["orgao"] for p in corpo["projetos_lei"]} == {"Plenário"}
    assert all(p["no_plenario"] for p in corpo["projetos_lei"])


def test_agenda_ignora_eventos_nao_deliberativos_e_cancelados(client, camara):
    client.get(f"/api/legislation/agenda?data={DATA}")

    assert ProjetoLei.query.count() == 2


def test_agenda_ignora_tipos_que_nao_sao_projetos_de_lei(client, camara):
    client.get(f"/api/legislation/agenda?data={DATA}")

    codigos = {p.codigo_pl for p in ProjetoLei.query.all()}
    assert not any(c.startswith(("TVR", "REQ")) for c in codigos)


def test_agenda_de_data_passada_usa_cache(client, camara):
    client.get("/api/legislation/agenda?data=2026-11-10")
    client.get("/api/legislation/agenda?data=2026-11-10")

    assert camara["eventos"] == 1


def test_falha_da_camara_retorna_502_e_nao_grava_agenda(client, monkeypatch, app):
    def falhar(data):
        raise ErroServicoExterno("API da Câmara indisponível no momento.")

    monkeypatch.setattr(integracoes, "eventos_do_dia", falhar)
    monkeypatch.setattr(integracoes, "feriados_do_ano", lambda ano: [])

    resposta = client.get(f"/api/legislation/agenda?data={DATA}")

    assert resposta.status_code == 502
    assert Agenda.query.count() == 0


def test_falha_nos_feriados_nao_derruba_a_agenda(client, camara, monkeypatch):
    def falhar(ano):
        raise ErroServicoExterno("Brasil API indisponível no momento.")

    monkeypatch.setattr(integracoes, "feriados_do_ano", falhar)

    resposta = client.get(f"/api/legislation/agenda?data={DATA}")

    assert resposta.status_code == 200
    assert resposta.json["dias_especiais"] == []


def test_agenda_futura_vazia_e_consultada_novamente(client, monkeypatch):
    chamadas = []
    futuro = (date.today() + timedelta(days=3)).isoformat()
    monkeypatch.setattr(integracoes, "eventos_do_dia", lambda data: chamadas.append(data) or [])
    monkeypatch.setattr(integracoes, "pautas_dos_eventos", lambda ids: [])
    monkeypatch.setattr(integracoes, "feriados_do_ano", lambda ano: [])

    client.get(f"/api/legislation/agenda?data={futuro}")
    client.get(f"/api/legislation/agenda?data={futuro}")

    assert len(chamadas) == 2


def test_projetos_de_parlamentar_seguido_aparecem_destacados(usuario_logado, camara, parlamentar):
    usuario_logado.post(f"/api/legislation/parlamentares/{parlamentar.id}/seguir")

    corpo = usuario_logado.get(f"/api/legislation/agenda?data={DATA}").json
    assert corpo["projetos_lei"][0]["destacado"] is True
    assert corpo["projetos_lei"][1]["destacado"] is False

    filtrado = usuario_logado.get(f"/api/legislation/agenda?data={DATA}&apenas_seguidos=true").json
    assert [p["codigo_pl"] for p in filtrado["projetos_lei"]] == ["PL 479/2025"]


def test_autores_so_sao_vinculados_a_projetos_do_plenario(client, camara, monkeypatch, parlamentar):
    consultados = []

    def autores(ids):
        consultados.extend(ids)
        return {i: [100] for i in ids}

    monkeypatch.setattr(integracoes, "autores_das_proposicoes", autores)
    monkeypatch.setattr(integracoes, "eventos_do_dia", lambda data: [{**EVENTOS[0], "orgaos": [{"nome": "CCJ", "sigla": "CCJC"}]}])

    client.get(f"/api/legislation/agenda?data={DATA}")

    assert consultados == []


def test_detalhe_do_projeto_lista_autores(client, camara, parlamentar):
    agenda = client.get(f"/api/legislation/agenda?data={DATA}").json
    projeto_id = agenda["projetos_lei"][0]["id"]

    detalhe = client.get(f"/api/legislation/projetos/{projeto_id}").json

    assert detalhe["parlamentares"][0]["nome"] == "Maria Souza"
    assert detalhe["parlamentares"][0]["posicionamento"] == "Autor"


def test_detalhe_de_projeto_inexistente_retorna_404(client):
    assert client.get("/api/legislation/projetos/999").status_code == 404
