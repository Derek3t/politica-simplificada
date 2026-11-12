from datetime import date, time

import pytest

from politica.extensions import db
from politica.legislation.models import Agenda, DiaEspecial, Parlamentar, ProjetoLei, Votacao


@pytest.fixture
def dados(app):
    agenda = Agenda(data=date(2026, 11, 10))
    agenda.projetos_lei.append(
        ProjetoLei(codigo_pl="PL 10/2026", titulo="Dispõe sobre o transporte público", no_plenario=True)
    )
    agenda.dias_especiais.append(DiaEspecial(nome="Dia do Transporte", tipo="national"))
    db.session.add_all(
        [
            agenda,
            Parlamentar(id_original=1, nome="Carlos Dias", partido="PL", estado="SP"),
            Votacao(
                id_original="1-1",
                data=date(2026, 11, 10),
                horario=time(15, 0),
                objeto="PL 10/2026",
                descricao="Aprovado o projeto sobre transporte.",
                aprovada=True,
            ),
        ]
    )
    db.session.commit()


def test_busca_encontra_em_todas_as_fontes(client, dados):
    corpo = client.get("/api/legislation/busca?q=transporte").json

    assert [p["codigo_pl"] for p in corpo["projetos"]] == ["PL 10/2026"]
    assert corpo["projetos"][0]["data"] == "2026-11-10"
    assert [d["nome"] for d in corpo["dias_especiais"]] == ["Dia do Transporte"]
    assert len(corpo["votacoes"]) == 1
    assert corpo["parlamentares"] == []


def test_busca_por_nome_de_parlamentar(client, dados):
    corpo = client.get("/api/legislation/busca?q=carlos").json

    assert [p["nome"] for p in corpo["parlamentares"]] == ["Carlos Dias"]
    assert corpo["projetos"] == []


def test_busca_exige_termo_com_dois_caracteres(client):
    assert client.get("/api/legislation/busca?q=a").status_code == 422
    assert client.get("/api/legislation/busca").status_code == 422


@pytest.mark.parametrize("termo", ["%%", "__", "a%"])
def test_busca_trata_curingas_do_sql_como_texto(client, dados, termo):
    corpo = client.get(f"/api/legislation/busca?q={termo}").json

    assert all(lista == [] for lista in corpo.values())


def test_listagem_de_parlamentares_trata_curinga_como_texto(client, dados):
    assert client.get("/api/legislation/parlamentares?busca=%25").json["total"] == 0


def test_filtro_de_partido_nao_aceita_curinga(client, dados):
    assert client.get("/api/legislation/parlamentares?partido=P%25").json["total"] == 0
    assert client.get("/api/legislation/parlamentares?partido=pl").json["total"] == 1
