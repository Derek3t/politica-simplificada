from datetime import date

import pytest

from politica.extensions import db
from politica.legislation import integracoes
from politica.legislation.models import Agenda, DiaEspecial, ProjetoLei


@pytest.fixture
def projeto(app):
    agenda = Agenda(data=date(2026, 11, 10))
    agenda.projetos_lei.append(ProjetoLei(codigo_pl="PL 1/2026", titulo="Ementa do projeto"))
    agenda.dias_especiais.append(DiaEspecial(nome="Dia Teste", tipo="national"))
    db.session.add(agenda)
    db.session.commit()
    return agenda


def test_analisar_exige_login(client, projeto):
    assert client.post(f"/api/legislation/projetos/{projeto.projetos_lei[0].id}/analisar").status_code == 401


def test_analisar_sem_chave_retorna_503(usuario_logado, projeto):
    resposta = usuario_logado.post(f"/api/legislation/projetos/{projeto.projetos_lei[0].id}/analisar")

    assert resposta.status_code == 503


def test_analisar_salva_resultado_e_nao_repete_chamada(usuario_logado, projeto, monkeypatch):
    chamadas = []

    def analisar(texto):
        chamadas.append(texto)
        return {"resumo": "Resumo simples", "analise_impacto": "Impacto", "comparacao_internacional": "Outros países"}

    monkeypatch.setattr(integracoes, "analisar_com_gemini", analisar)
    url = f"/api/legislation/projetos/{projeto.projetos_lei[0].id}/analisar"

    assert usuario_logado.post(url).json["resumo"] == "Resumo simples"
    usuario_logado.post(url)

    assert chamadas == ["Ementa do projeto"]


def test_contextualizar_dia_especial(usuario_logado, projeto, monkeypatch):
    monkeypatch.setattr(
        integracoes,
        "contextualizar_dia_especial",
        lambda nome, data: {"contexto_historico": "Origem", "importancia": "Relevante", "impacto_legislativo": "Leis"},
    )

    resposta = usuario_logado.post(f"/api/legislation/dias-especiais/{projeto.dias_especiais[0].id}/contextualizar")

    assert resposta.status_code == 200
    assert resposta.json["contexto_historico"] == "Origem"
