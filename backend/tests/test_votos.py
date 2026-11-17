from datetime import date, timedelta

import pytest

from politica.errors import ErroServicoExterno
from politica.extensions import db
from politica.legislation import integracoes
from politica.legislation.models import Agenda, Historico, Parlamentar, ProjetoLei, Votacao, VotoParlamentar

HOJE = date.today()


@pytest.fixture
def deputados(app):
    ana = Parlamentar(id_original=1, nome="Ana Lima", partido="PT", estado="ES")
    bia = Parlamentar(id_original=2, nome="Bia Souza", partido="PL", estado="SP")
    db.session.add_all([ana, bia])
    db.session.commit()
    return ana, bia


@pytest.fixture
def votacoes(app):
    nominal = Votacao(id_original="v-1", data=HOJE, objeto="PL 10/2026", descricao="Votação nominal", aprovada=True)
    simbolica = Votacao(id_original="v-2", data=HOJE - timedelta(days=1), objeto="PL 11/2026", descricao="Simbólica")
    db.session.add_all([nominal, simbolica])
    db.session.commit()
    return nominal, simbolica


@pytest.fixture
def camara(monkeypatch):
    chamadas = []

    def votos(ids):
        chamadas.append(list(ids))
        nominal = [
            {"id_deputado": 1, "voto": "Sim"},
            {"id_deputado": 2, "voto": "Não"},
            {"id_deputado": 99, "voto": "Sim"},
        ]
        return {i: nominal if i == "v-1" else [] for i in ids}

    monkeypatch.setattr(integracoes, "votos_de_votacoes", votos)
    monkeypatch.setattr(integracoes, "votacoes_do_periodo", lambda inicio, fim: [])
    return chamadas


def test_perfil_mostra_historico_de_votos_do_parlamentar(client, deputados, votacoes, camara):
    ana, _ = deputados

    perfil = client.get(f"/api/legislation/parlamentares/{ana.id}").json

    assert perfil["nome"] == "Ana Lima"
    assert perfil["resumo_votos"] == {"Sim": 1}
    assert [(v["objeto"], v["voto"]) for v in perfil["votos"]] == [("PL 10/2026", "Sim")]


def test_votos_sao_baixados_uma_unica_vez(client, deputados, votacoes, camara):
    ana, bia = deputados

    client.get(f"/api/legislation/parlamentares/{ana.id}")
    client.get(f"/api/legislation/parlamentares/{bia.id}")

    assert len(camara) == 1
    assert VotoParlamentar.query.count() == 2


def test_voto_de_deputado_desconhecido_e_ignorado(client, deputados, votacoes, camara):
    client.get(f"/api/legislation/parlamentares/{deputados[0].id}")

    assert {v.voto for v in VotoParlamentar.query} == {"Sim", "Não"}


def test_perfil_lista_projetos_de_autoria(client, deputados, camara):
    ana, _ = deputados
    agenda = Agenda(data=HOJE)
    projeto = ProjetoLei(codigo_pl="PL 5/2026", titulo="Ementa", data_votacao=HOJE)
    agenda.projetos_lei.append(projeto)
    projeto.historicos.append(Historico(parlamentar_id=ana.id, posicionamento="Autor"))
    db.session.add(agenda)
    db.session.commit()

    perfil = client.get(f"/api/legislation/parlamentares/{ana.id}").json

    assert [a["codigo_pl"] for a in perfil["autorias"]] == ["PL 5/2026"]


def test_perfil_sobrevive_a_camara_fora_do_ar(client, deputados, votacoes, monkeypatch):
    def falhar(*args):
        raise ErroServicoExterno("fora do ar")

    monkeypatch.setattr(integracoes, "votos_de_votacoes", falhar)
    monkeypatch.setattr(integracoes, "votacoes_do_periodo", falhar)

    resposta = client.get(f"/api/legislation/parlamentares/{deputados[0].id}")

    assert resposta.status_code == 200
    assert resposta.json["votos"] == []


def test_perfil_inexistente_retorna_404(client):
    assert client.get("/api/legislation/parlamentares/999").status_code == 404


def test_votacao_detalhada_traz_placar_e_votos_dos_seguidos(usuario_logado, deputados, votacoes, camara):
    ana, _ = deputados
    usuario_logado.post(f"/api/legislation/parlamentares/{ana.id}/seguir")

    detalhe = usuario_logado.get(f"/api/legislation/votacoes/{votacoes[0].id}").json

    assert detalhe["nominal"] is True
    assert detalhe["placar"] == {"Sim": 1, "Não": 1}
    assert [(p["nome"], p["voto"]) for p in detalhe["votos_seguidos"]] == [("Ana Lima", "Sim")]


def test_votacao_simbolica_nao_tem_placar(client, deputados, votacoes, camara):
    detalhe = client.get(f"/api/legislation/votacoes/{votacoes[1].id}").json

    assert detalhe["nominal"] is False
    assert detalhe["votos_seguidos"] == []


def test_votacao_inexistente_retorna_404(client):
    assert client.get("/api/legislation/votacoes/999").status_code == 404
