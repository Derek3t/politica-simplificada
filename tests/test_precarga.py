from datetime import date, timedelta

import pytest

from politica.errors import ErroServicoExterno
from politica.legislation import integracoes
from politica.legislation.models import Agenda, DiaEspecial, Parlamentar, ProjetoLei, Votacao
from politica.precarga import datas_da_janela, precarregar

HOJE = date(2026, 11, 11)

EVENTO = {
    "id": 1,
    "descricaoTipo": "Sessão Deliberativa",
    "situacao": "Convocada",
    "dataHoraInicio": "2026-11-11T14:00",
    "orgaos": [{"nome": "Plenário", "sigla": "PLEN"}],
}
PAUTA = [{"proposicao_": {"id": 10, "siglaTipo": "PL", "numero": 1, "ano": 2026, "ementa": "Ementa do projeto."}}]


@pytest.fixture
def camara(app, monkeypatch):
    chamadas = {"deputados": 0, "eventos": []}

    def deputados():
        chamadas["deputados"] += 1
        return [
            {"id": 1, "nome": "Ana", "siglaPartido": "PT", "siglaUf": "ES"},
            {"id": 2, "nome": "Bia", "siglaPartido": "PL", "siglaUf": "SP"},
        ]

    def eventos(dia):
        chamadas["eventos"].append(dia)
        return [EVENTO]

    monkeypatch.setattr(integracoes, "listar_deputados", deputados)
    monkeypatch.setattr(integracoes, "eventos_do_dia", eventos)
    monkeypatch.setattr(integracoes, "pautas_dos_eventos", lambda ids: [PAUTA for _ in ids])
    monkeypatch.setattr(integracoes, "autores_das_proposicoes", lambda ids: {i: [1] for i in ids})
    monkeypatch.setattr(
        integracoes, "feriados_do_ano", lambda ano: [{"date": "2026-11-12", "name": "Dia Teste", "type": "national"}]
    )
    monkeypatch.setattr(
        integracoes,
        "votacoes_do_periodo",
        lambda inicio, fim: [
            {
                "id": "v-1",
                "data": "2026-11-10",
                "dataHoraRegistro": "2026-11-10T19:00:00",
                "proposicaoObjeto": "PL 1/2026",
                "descricao": "Aprovado o projeto.",
                "aprovacao": 1,
            }
        ],
    )
    return chamadas


@pytest.fixture
def mensagens():
    return []


def rodar(mensagens, **opcoes):
    return precarregar(hoje=HOJE, passados=1, futuros=1, avisar=mensagens.append, **opcoes)


def test_janela_inclui_passados_hoje_e_futuros():
    datas = datas_da_janela(HOJE, 2, 3)

    assert datas[0] == HOJE - timedelta(days=2)
    assert datas[-1] == HOJE + timedelta(days=3)
    assert len(datas) == 6


def test_precarga_completa_popula_o_banco(camara, mensagens):
    relatorio = rodar(mensagens)

    assert relatorio.parlamentares_importados == 2
    assert relatorio.agendas_carregadas == 3
    assert relatorio.projetos_plenario == 3
    assert relatorio.dias_especiais == 1
    assert relatorio.votacoes == 1
    assert not relatorio.tem_falhas
    assert Parlamentar.query.count() == 2
    assert Agenda.query.count() == 3
    assert Votacao.query.count() == 1


def test_parlamentares_sao_importados_antes_das_agendas_para_vincular_autores(camara, mensagens):
    rodar(mensagens)

    assert sum(len(projeto.historicos) for projeto in ProjetoLei.query.all()) == 3


def test_segunda_execucao_nao_duplica_nem_reimporta(camara, mensagens):
    rodar(mensagens)
    segunda = rodar(mensagens)

    assert camara["deputados"] == 1
    assert segunda.parlamentares_importados is None
    assert Parlamentar.query.count() == 2
    assert ProjetoLei.query.count() == 3
    assert Agenda.query.count() == 3


def test_forcar_reimporta_parlamentares(camara, mensagens):
    rodar(mensagens)
    rodar(mensagens, forcar_parlamentares=True)

    assert camara["deputados"] == 2
    assert Parlamentar.query.count() == 2


def test_falha_em_um_dia_nao_interrompe_os_demais(camara, mensagens, monkeypatch):
    def eventos(dia):
        if dia == HOJE:
            raise ErroServicoExterno("API da Câmara indisponível no momento.")
        return [EVENTO]

    monkeypatch.setattr(integracoes, "eventos_do_dia", eventos)

    relatorio = rodar(mensagens)

    assert relatorio.falhas_agenda == [HOJE]
    assert relatorio.agendas_carregadas == 2
    assert relatorio.tem_falhas
    assert Agenda.query.count() == 2


def test_falha_nos_parlamentares_nao_impede_o_resto(camara, mensagens, monkeypatch):
    def falhar():
        raise ErroServicoExterno("API da Câmara indisponível no momento.")

    monkeypatch.setattr(integracoes, "listar_deputados", falhar)

    relatorio = rodar(mensagens)

    assert relatorio.falha_parlamentares
    assert relatorio.agendas_carregadas == 3
    assert relatorio.tem_falhas


def test_falha_nas_votacoes_e_registrada(camara, mensagens, monkeypatch):
    def falhar(inicio, fim):
        raise ErroServicoExterno("API da Câmara indisponível no momento.")

    monkeypatch.setattr(integracoes, "votacoes_do_periodo", falhar)

    relatorio = rodar(mensagens)

    assert relatorio.falha_votacoes
    assert relatorio.agendas_carregadas == 3


def test_ia_sem_chave_pula_a_etapa_sem_erro(camara, mensagens):
    relatorio = rodar(mensagens, com_ia=True)

    assert relatorio.ia_indisponivel
    assert relatorio.resumos_gerados == 0
    assert not relatorio.tem_falhas
    assert any("Etapa pulada" in mensagem for mensagem in mensagens)


def test_ia_gera_resumos_respeitando_o_limite(camara, mensagens, monkeypatch):
    analisados = []

    def analisar(texto):
        analisados.append(texto)
        return {"resumo": "Resumo", "analise_impacto": "Impacto", "comparacao_internacional": "Mundo"}

    monkeypatch.setattr(integracoes, "analisar_com_gemini", analisar)
    monkeypatch.setattr(
        integracoes,
        "contextualizar_dia_especial",
        lambda nome, data: {"contexto_historico": "a", "importancia": "b", "impacto_legislativo": "c"},
    )

    relatorio = rodar(mensagens, com_ia=True, limite_ia=2)

    assert relatorio.resumos_gerados == 2
    assert relatorio.dias_explicados == 1
    assert ProjetoLei.query.filter(ProjetoLei.resumo.is_not(None)).count() == 2
    assert DiaEspecial.query.filter(DiaEspecial.contexto_historico.is_not(None)).count() == 1


def test_ia_prioriza_os_dias_mais_proximos_de_hoje(camara, mensagens, monkeypatch):
    monkeypatch.setattr(
        integracoes,
        "analisar_com_gemini",
        lambda texto: {"resumo": "r", "analise_impacto": "i", "comparacao_internacional": "c"},
    )

    rodar(mensagens, com_ia=True, limite_ia=1)

    resumido = ProjetoLei.query.filter(ProjetoLei.resumo.is_not(None)).one()
    assert resumido.agenda.data == HOJE


def test_falha_da_ia_em_um_item_nao_para_os_outros(camara, mensagens, monkeypatch):
    def analisar(texto):
        raise ErroServicoExterno("Não foi possível gerar a análise com IA.")

    monkeypatch.setattr(integracoes, "analisar_com_gemini", analisar)
    monkeypatch.setattr(
        integracoes,
        "contextualizar_dia_especial",
        lambda nome, data: {"contexto_historico": "a", "importancia": "b", "impacto_legislativo": "c"},
    )

    relatorio = rodar(mensagens, com_ia=True, limite_ia=2)

    assert relatorio.falhas_ia == 2
    assert relatorio.dias_explicados == 1


def test_comando_exibe_resumo_e_sai_com_sucesso(camara, app):
    resultado = app.test_cli_runner().invoke(args=["precarregar", "--passados", "0", "--futuros", "1"])

    assert resultado.exit_code == 0
    assert "Resumo: 2 agendas" in resultado.output


def test_comando_sai_com_erro_quando_alguma_etapa_falha(camara, app, monkeypatch):
    def falhar(dia):
        raise ErroServicoExterno("API da Câmara indisponível no momento.")

    monkeypatch.setattr(integracoes, "eventos_do_dia", falhar)

    resultado = app.test_cli_runner().invoke(args=["precarregar", "--passados", "0", "--futuros", "0"])

    assert resultado.exit_code == 1
    assert "Rode o comando de novo" in resultado.output


@pytest.mark.parametrize("opcao", ["--passados=-1", "--futuros=61", "--limite-ia=51"])
def test_comando_rejeita_opcoes_fora_do_intervalo(app, opcao):
    resultado = app.test_cli_runner().invoke(args=["precarregar", opcao])

    assert resultado.exit_code == 2
