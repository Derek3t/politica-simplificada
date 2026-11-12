import logging
from datetime import date, timedelta

from sqlalchemy import func, select

from politica.errors import ErroApi
from politica.extensions import db
from politica.legislation import services
from politica.legislation.models import Agenda, DiaEspecial, Parlamentar, ProjetoLei, Votacao

logger = logging.getLogger(__name__)

STATUS_SEM_CHAVE = 503


class Relatorio:
    def __init__(self):
        self.parlamentares_importados = None
        self.falha_parlamentares = False
        self.agendas_carregadas = 0
        self.projetos = 0
        self.projetos_plenario = 0
        self.dias_especiais = 0
        self.falhas_agenda = []
        self.votacoes = 0
        self.falha_votacoes = False
        self.resumos_gerados = 0
        self.dias_explicados = 0
        self.falhas_ia = 0
        self.ia_indisponivel = False

    @property
    def tem_falhas(self):
        return self.falha_parlamentares or self.falha_votacoes or bool(self.falhas_agenda)


def datas_da_janela(hoje, passados, futuros):
    return [hoje + timedelta(days=deslocamento) for deslocamento in range(-passados, futuros + 1)]


def precarregar_parlamentares(relatorio, forcar, avisar):
    existentes = db.session.scalar(select(func.count()).select_from(Parlamentar))
    if existentes and not forcar:
        avisar(f"Parlamentares: {existentes} já importados, pulando.")
        return
    avisar("Parlamentares: importando da Câmara...")
    try:
        criados, atualizados = services.importar_parlamentares()
    except ErroApi as erro:
        relatorio.falha_parlamentares = True
        avisar(f"Parlamentares: falhou ({erro.mensagem})")
        return
    relatorio.parlamentares_importados = criados + atualizados
    avisar(f"Parlamentares: {criados} novos, {atualizados} atualizados.")


def precarregar_agendas(relatorio, datas, avisar):
    for posicao, dia in enumerate(datas, 1):
        try:
            agenda = services.obter_ou_criar_agenda(dia)
        except ErroApi as erro:
            relatorio.falhas_agenda.append(dia)
            avisar(f"Agenda {dia} ({posicao}/{len(datas)}): falhou ({erro.mensagem})")
            continue
        no_plenario = sum(projeto.no_plenario for projeto in agenda.projetos_lei)
        relatorio.agendas_carregadas += 1
        relatorio.projetos += len(agenda.projetos_lei)
        relatorio.projetos_plenario += no_plenario
        relatorio.dias_especiais += len(agenda.dias_especiais)
        avisar(
            f"Agenda {dia} ({posicao}/{len(datas)}): {len(agenda.projetos_lei)} projetos, {no_plenario} no Plenário."
        )


def precarregar_votacoes(relatorio, hoje, avisar):
    inicio = hoje - timedelta(days=services.DIAS_POR_PERIODO["mes"])
    avisar(f"Votações: sincronizando de {inicio} a {hoje}...")
    try:
        services.sincronizar_votacoes(inicio, hoje)
    except ErroApi as erro:
        relatorio.falha_votacoes = True
        avisar(f"Votações: falhou ({erro.mensagem})")
        return
    relatorio.votacoes = db.session.scalar(
        select(func.count()).select_from(Votacao).where(Votacao.data.between(inicio, hoje))
    )
    avisar(f"Votações: {relatorio.votacoes} de mérito no período.")


def mais_proximos(itens, hoje, limite):
    return sorted(itens, key=lambda item: abs((item.agenda.data - hoje).days))[:limite]


def precarregar_ia(relatorio, hoje, datas, limite, avisar):
    projetos = db.session.scalars(
        select(ProjetoLei)
        .join(Agenda)
        .where(ProjetoLei.no_plenario.is_(True), ProjetoLei.resumo.is_(None), Agenda.data.between(datas[0], datas[-1]))
    ).all()
    dias = db.session.scalars(
        select(DiaEspecial)
        .join(Agenda)
        .where(DiaEspecial.contexto_historico.is_(None), Agenda.data.between(datas[0], datas[-1]))
    ).all()

    avisar(f"IA: gerando até {limite} resumos de projetos e {limite} contextos de datas...")
    tarefas = [(services.analisar_projeto, item) for item in mais_proximos(projetos, hoje, limite)]
    tarefas += [(services.contextualizar_dia_especial, item) for item in mais_proximos(dias, hoje, limite)]

    for funcao, item in tarefas:
        try:
            funcao(item)
        except ErroApi as erro:
            if erro.status == STATUS_SEM_CHAVE:
                relatorio.ia_indisponivel = True
                avisar(f"IA: {erro.mensagem} Etapa pulada.")
                return
            relatorio.falhas_ia += 1
            avisar(f"IA: falhou em {getattr(item, 'codigo_pl', None) or item.nome} ({erro.mensagem})")
            continue
        if isinstance(item, ProjetoLei):
            relatorio.resumos_gerados += 1
        else:
            relatorio.dias_explicados += 1
    avisar(f"IA: {relatorio.resumos_gerados} resumos e {relatorio.dias_explicados} contextos gerados.")


def precarregar(hoje=None, passados=7, futuros=10, forcar_parlamentares=False, com_ia=False, limite_ia=5, avisar=None):
    hoje = hoje or date.today()
    avisar = avisar or logger.info
    datas = datas_da_janela(hoje, passados, futuros)
    relatorio = Relatorio()

    precarregar_parlamentares(relatorio, forcar_parlamentares, avisar)
    precarregar_agendas(relatorio, datas, avisar)
    precarregar_votacoes(relatorio, hoje, avisar)
    if com_ia:
        precarregar_ia(relatorio, hoje, datas, limite_ia, avisar)
    return relatorio
