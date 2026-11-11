from datetime import date

import pytest

from politica.errors import ErroServicoExterno
from politica.extensions import db
from politica.legislation import integracoes
from politica.legislation.models import Agenda, ProjetoLei, Votacao

MES = date.today().strftime("%Y-%m")
PRIMEIRO_DIA = f"{MES}-01"


@pytest.fixture
def feriados(monkeypatch):
    chamadas = []

    def buscar(ano):
        chamadas.append(ano)
        return [
            {"date": PRIMEIRO_DIA, "name": "Dia Teste", "type": "national"},
            {"date": f"{ano}-01-01" if MES[5:] != "01" else f"{ano}-02-01", "name": "Outro mês", "type": "national"},
        ]

    monkeypatch.setattr(integracoes, "feriados_do_ano", buscar)
    monkeypatch.setattr(integracoes, "votacoes_do_periodo", lambda inicio, fim: [])
    return chamadas


def popular():
    agenda = Agenda(data=date.fromisoformat(PRIMEIRO_DIA))
    agenda.projetos_lei.extend(
        [
            ProjetoLei(codigo_pl="PL 1/2026", titulo="a", no_plenario=True),
            ProjetoLei(codigo_pl="PL 2/2026", titulo="b", no_plenario=True),
            ProjetoLei(codigo_pl="PL 3/2026", titulo="c", no_plenario=False),
        ]
    )
    db.session.add(agenda)
    db.session.add(
        Votacao(id_original="v-1", data=date.fromisoformat(PRIMEIRO_DIA), descricao="Aprovado o PL", aprovada=True)
    )
    db.session.commit()


def test_calendario_combina_feriados_votacoes_e_projetos(client, feriados):
    popular()

    corpo = client.get(f"/api/legislation/calendario?mes={MES}").json

    assert corpo["mes"] == MES
    assert corpo["dias"][PRIMEIRO_DIA] == {"feriados": ["Dia Teste"], "votacoes": 1, "projetos": 2}


def test_calendario_so_inclui_dias_com_conteudo(client, feriados):
    corpo = client.get(f"/api/legislation/calendario?mes={MES}").json

    assert list(corpo["dias"]) == [PRIMEIRO_DIA]


def test_calendario_nao_inclui_feriados_de_outros_meses(client, feriados):
    corpo = client.get(f"/api/legislation/calendario?mes={MES}").json

    assert all(dia.startswith(MES) for dia in corpo["dias"])


def test_feriados_do_ano_sao_consultados_uma_vez(client, feriados):
    client.get(f"/api/legislation/calendario?mes={MES}")
    client.get(f"/api/legislation/calendario?mes={MES}")

    assert len(feriados) == 1


def test_calendario_funciona_sem_feriados_e_sem_camara(client, monkeypatch):
    def falhar(*argumentos):
        raise ErroServicoExterno("indisponível")

    monkeypatch.setattr(integracoes, "feriados_do_ano", falhar)
    monkeypatch.setattr(integracoes, "votacoes_do_periodo", falhar)
    popular()

    resposta = client.get(f"/api/legislation/calendario?mes={MES}")

    assert resposta.status_code == 200
    assert resposta.json["dias"][PRIMEIRO_DIA] == {"feriados": [], "votacoes": 1, "projetos": 2}


def test_mes_futuro_nao_consulta_votacoes(client, feriados, monkeypatch):
    consultas = []
    monkeypatch.setattr(integracoes, "votacoes_do_periodo", lambda i, f: consultas.append((i, f)) or [])

    client.get("/api/legislation/calendario?mes=2099-01")

    assert consultas == []


@pytest.mark.parametrize("mes", ["2026-13", "2026-1", "novembro", "2026-00", ""])
def test_valida_formato_do_mes(client, mes):
    resposta = client.get(f"/api/legislation/calendario?mes={mes}")

    assert resposta.status_code == 422
    assert "mes" in resposta.json["detalhes"]


def test_mes_e_obrigatorio(client):
    assert client.get("/api/legislation/calendario").status_code == 422
