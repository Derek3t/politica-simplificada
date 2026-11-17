import calendar
import logging
from datetime import date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from politica.auth.models import UsuarioParlamentar
from politica.errors import ErroApi, ErroServicoExterno
from politica.extensions import db
from politica.legislation import integracoes, senado, votos
from politica.legislation.datas_civicas import contexto_do_feriado, dias_especiais_extras
from politica.legislation.models import Agenda, DiaEspecial, Historico, Parlamentar, ProjetoLei, Votacao

logger = logging.getLogger(__name__)

SIGLA_PLENARIO = "PLEN"
DIAS_POR_PERIODO = {"hoje": 0, "semana": 6, "mes": 29}
DIAS_HISTORICO = 89
INTERVALO_SINCRONIZACAO = timedelta(minutes=10)
TERMOS_DE_PROJETO = ("projeto de lei", "proposta de emenda", "medida provisória", "projeto de decreto legislativo")
TERMOS_PROCEDIMENTAIS = ("requerimento", "regime de tramitação")
STATUS_VOTACAO = {"aprovado": True, "rejeitado": False}
sincronizacoes_votacoes = {}
cache_feriados = {}
LIMITE_BUSCA = 10
TIPOS_RELEVANTES = {"PL", "PLP", "PEC", "PDL", "MPV", "PLN", "PLV"}


def eh_deliberativo(evento):
    tipo = evento.get("descricaoTipo", "").lower()
    cancelado = evento.get("situacao", "").lower().startswith("cancelad")
    return "deliberativ" in tipo and "não deliberativ" not in tipo and not cancelado


def feriados_do_ano(ano):
    if ano not in cache_feriados:
        cache_feriados[ano] = integracoes.feriados_do_ano(ano)
    return cache_feriados[ano]


def carregar_feriados(agenda):
    try:
        feriados = feriados_do_ano(agenda.data.year)
    except ErroServicoExterno:
        return
    for feriado in feriados:
        if feriado.get("date") == agenda.data.isoformat():
            agenda.dias_especiais.append(DiaEspecial(nome=feriado["name"], tipo=feriado.get("type", "nacional")))


def horario_do_evento(evento):
    try:
        return datetime.fromisoformat(evento["dataHoraInicio"]).time()
    except (KeyError, TypeError, ValueError):
        return None


def vincular_autores(projetos):
    autores = integracoes.autores_das_proposicoes([int(p.id_original) for p in projetos])
    ids_deputados = {id_dep for lista in autores.values() for id_dep in lista}
    parlamentares = db.session.execute(
        select(Parlamentar.id_original, Parlamentar.id).where(
            Parlamentar.casa == "Câmara", Parlamentar.id_original.in_(ids_deputados)
        )
    ).all()
    mapa = dict(parlamentares)

    for projeto in projetos:
        for id_deputado in autores[int(projeto.id_original)]:
            if id_deputado in mapa:
                projeto.historicos.append(Historico(parlamentar_id=mapa[id_deputado], posicionamento="Autor"))


def criar_projeto(proposicao, item, evento, data, no_plenario):
    sigla = proposicao.get("siglaTipo")
    return ProjetoLei(
        id_original=str(proposicao["id"]),
        tipo=sigla,
        codigo_pl=f"{sigla} {proposicao.get('numero')}/{proposicao.get('ano')}",
        titulo=proposicao.get("ementa") or item.get("topico") or "Sem ementa",
        orgao=(evento.get("orgaos") or [{}])[0].get("nome"),
        horario=horario_do_evento(evento),
        no_plenario=no_plenario,
        status=item.get("situacaoItem") or "Em pauta",
        data_votacao=data,
    )


def carregar_pauta(agenda):
    eventos = [e for e in integracoes.eventos_do_dia(agenda.data) if eh_deliberativo(e)]
    pautas = integracoes.pautas_dos_eventos([e["id"] for e in eventos])

    existentes = {p.id_original for p in agenda.projetos_lei}
    novos, do_plenario = [], []
    for evento, itens in zip(eventos, pautas, strict=True):
        no_plenario = (evento.get("orgaos") or [{}])[0].get("sigla") == SIGLA_PLENARIO
        for item in itens:
            proposicao = item.get("proposicaoRelacionada_") or item.get("proposicao_")
            if not proposicao or proposicao.get("siglaTipo") not in TIPOS_RELEVANTES:
                continue
            if str(proposicao["id"]) in existentes:
                continue
            existentes.add(str(proposicao["id"]))
            projeto = criar_projeto(proposicao, item, evento, agenda.data, no_plenario)
            novos.append(projeto)
            if no_plenario:
                do_plenario.append(projeto)

    agenda.projetos_lei.extend(novos)
    vincular_autores(do_plenario)


def obter_ou_criar_agenda(data: date) -> Agenda:
    agenda = db.session.scalar(select(Agenda).where(Agenda.data == data))
    if agenda and (agenda.projetos_lei or data < date.today()):
        return agenda

    try:
        agenda = agenda or Agenda(data=data)
        db.session.add(agenda)
        db.session.flush()
        if not agenda.dias_especiais:
            carregar_feriados(agenda)
        carregar_pauta(agenda)
        db.session.commit()
    except ErroServicoExterno:
        db.session.rollback()
        raise
    except IntegrityError:
        db.session.rollback()
        return db.session.scalar(select(Agenda).where(Agenda.data == data))
    return agenda


def ids_seguidos(usuario):
    if usuario is None:
        return set()
    return {s.parlamentar_id for s in usuario.parlamentares_seguidos}


def montar_agenda(agenda, usuario, apenas_seguidos=False, incluir_comissoes=False, uf=None):
    seguidos = ids_seguidos(usuario)
    projetos = []
    for projeto in agenda.projetos_lei:
        if not incluir_comissoes and not projeto.no_plenario:
            continue
        destacado = any(h.parlamentar_id in seguidos for h in projeto.historicos)
        if apenas_seguidos and not destacado:
            continue
        projetos.append(projeto.to_dict(destacado))
    projetos.sort(key=lambda p: (not p["destacado"], p["horario"] or "99:99"))

    return {
        "id": agenda.id,
        "data": agenda.data.isoformat(),
        "dias_especiais": [d.to_dict() for d in agenda.dias_especiais] + dias_especiais_extras(agenda.data, uf),
        "projetos_lei": projetos,
        "votacoes": [] if apenas_seguidos else votacoes_do_dia(agenda.data, incluir_camara=not projetos),
    }


def votacoes_do_dia(dia, incluir_camara):
    """Votações já sincronizadas do dia. A pauta da Câmara já cobre as votações dela, então as da Câmara só
    entram quando a pauta do dia está vazia; o Senado não tem pauta própria e sempre aparece."""
    consulta = select(Votacao).where(Votacao.data == dia).order_by(Votacao.horario, Votacao.id)
    if not incluir_camara:
        consulta = consulta.where(Votacao.casa == "Senado")
    return [v.to_dict() for v in db.session.scalars(consulta)]


def detalhar_projeto(projeto, usuario):
    seguidos = ids_seguidos(usuario)
    detalhe = projeto.to_dict(any(h.parlamentar_id in seguidos for h in projeto.historicos))
    detalhe["parlamentares"] = [
        {**h.parlamentar.to_dict(h.parlamentar_id in seguidos), "posicionamento": h.posicionamento}
        for h in projeto.historicos
    ]
    return detalhe


def analisar_projeto(projeto):
    if projeto.resumo:
        return projeto
    analise = integracoes.analisar_com_ia(projeto.titulo)
    for campo, valor in analise.items():
        setattr(projeto, campo, valor)
    db.session.commit()
    return projeto


def contextualizar_dia_especial(dia):
    if dia.contexto_historico or contexto_do_feriado(dia.nome):
        return dia
    contexto = integracoes.contextualizar_dia_especial(dia.nome, dia.agenda.data.strftime("%d/%m/%Y"))
    for campo, valor in contexto.items():
        setattr(dia, campo, valor)
    db.session.commit()
    return dia


def intervalo_do_periodo(periodo):
    fim = date.today()
    return fim - timedelta(days=DIAS_POR_PERIODO[periodo]), fim


def atualizar_votacao(votacao, dados):
    registro = datetime.fromisoformat(dados["dataHoraRegistro"]) if dados.get("dataHoraRegistro") else None
    votacao.data = date.fromisoformat(dados["data"])
    votacao.horario = registro.time() if registro else None
    votacao.objeto = dados.get("proposicaoObjeto")
    votacao.descricao = dados.get("descricao") or "Sem descrição"
    votacao.aprovada = {1: True, 0: False}.get(dados.get("aprovacao"))


def eh_votacao_de_projeto(dados):
    objeto = dados.get("proposicaoObjeto") or ""
    descricao = (dados.get("descricao") or "").lower()
    if any(termo in descricao for termo in TERMOS_PROCEDIMENTAIS):
        return False
    return objeto.split(" ")[0] in TIPOS_RELEVANTES or any(termo in descricao for termo in TERMOS_DE_PROJETO)


def sincronizar_votacoes(inicio, fim):
    ultima = sincronizacoes_votacoes.get((inicio, fim))
    if ultima and datetime.now() - ultima < INTERVALO_SINCRONIZACAO:
        return

    if not sincronizar_votacoes_camara(inicio, fim):
        return
    try:
        senado.sincronizar_votacoes_senado(inicio, fim, TIPOS_RELEVANTES)
    except ErroServicoExterno:
        db.session.rollback()
        logger.warning("Senado indisponível, exibindo votações já salvas de %s a %s", inicio, fim)
    sincronizacoes_votacoes[(inicio, fim)] = datetime.now()


def sincronizar_votacoes_camara(inicio, fim):
    try:
        recebidas = integracoes.votacoes_do_periodo(inicio, fim)
    except ErroServicoExterno:
        if db.session.scalar(select(Votacao.id).where(Votacao.data.between(inicio, fim)).limit(1)) is None:
            raise
        logger.warning("Câmara indisponível, exibindo votações já salvas de %s a %s", inicio, fim)
        return False

    existentes = {
        v.id_original: v
        for v in db.session.scalars(select(Votacao).where(Votacao.casa == "Câmara", Votacao.data.between(inicio, fim)))
    }
    for dados in recebidas:
        if not eh_votacao_de_projeto(dados):
            continue
        votacao = existentes.get(dados["id"])
        if votacao is None:
            votacao = Votacao(id_original=dados["id"])
            db.session.add(votacao)
        atualizar_votacao(votacao, dados)
    db.session.commit()
    return True


def dia_vazio():
    return {"feriados": [], "votacoes": 0, "projetos": 0}


def montar_calendario(mes, uf=None):
    ano, numero = (int(parte) for parte in mes.split("-"))
    inicio = date(ano, numero, 1)
    fim = date(ano, numero, calendar.monthrange(ano, numero)[1])
    dias = {}

    try:
        for feriado in feriados_do_ano(ano):
            if feriado["date"].startswith(mes):
                dias.setdefault(feriado["date"], dia_vazio())["feriados"].append(feriado["name"])
    except ErroServicoExterno:
        logger.warning("Feriados de %s indisponíveis para o calendário", ano)

    for numero_do_dia in range(1, fim.day + 1):
        for extra in dias_especiais_extras(date(ano, numero, numero_do_dia), uf):
            dias.setdefault(extra["data"], dia_vazio())["feriados"].append(extra["nome"])

    if inicio <= date.today():
        try:
            sincronizar_votacoes(inicio, min(fim, date.today()))
        except ErroServicoExterno:
            logger.warning("Votações de %s indisponíveis para o calendário", mes)

    votacoes = db.session.execute(
        select(Votacao.data, func.count()).where(Votacao.data.between(inicio, fim)).group_by(Votacao.data)
    )
    for dia, quantidade in votacoes:
        dias.setdefault(dia.isoformat(), dia_vazio())["votacoes"] = quantidade

    projetos = db.session.execute(
        select(Agenda.data, func.count(ProjetoLei.id))
        .join(ProjetoLei, ProjetoLei.agenda_id == Agenda.id)
        .where(Agenda.data.between(inicio, fim), ProjetoLei.no_plenario.is_(True))
        .group_by(Agenda.data)
    )
    for dia, quantidade in projetos:
        dias.setdefault(dia.isoformat(), dia_vazio())["projetos"] = quantidade

    return {"mes": mes, "dias": dict(sorted(dias.items()))}


def listar_votacoes(filtros):
    inicio, fim = intervalo_do_periodo(filtros.periodo)
    sincronizar_votacoes(inicio, fim)

    consulta = select(Votacao).where(Votacao.data.between(inicio, fim))
    if filtros.casa:
        consulta = consulta.where(Votacao.casa == filtros.casa)
    if filtros.status == "andamento":
        consulta = consulta.where(Votacao.aprovada.is_(None))
    elif filtros.status:
        consulta = consulta.where(Votacao.aprovada.is_(STATUS_VOTACAO[filtros.status]))
    consulta = consulta.order_by(Votacao.data.desc(), Votacao.horario.desc())

    paginacao = db.paginate(consulta, page=filtros.pagina, per_page=filtros.por_pagina, error_out=False)
    return {
        "itens": [v.to_dict() for v in paginacao.items],
        "pagina": paginacao.page,
        "total_paginas": paginacao.pages,
        "total": paginacao.total,
    }


def listar_parlamentares(filtros, usuario):
    consulta = select(Parlamentar).order_by(Parlamentar.nome)
    if filtros.casa:
        consulta = consulta.where(Parlamentar.casa == filtros.casa)
    if filtros.busca:
        consulta = consulta.where(Parlamentar.nome.icontains(filtros.busca, autoescape=True))
    if filtros.estado:
        consulta = consulta.where(Parlamentar.estado == filtros.estado.upper())
    if filtros.partido:
        consulta = consulta.where(func.lower(Parlamentar.partido) == filtros.partido.lower())

    paginacao = db.paginate(consulta, page=filtros.pagina, per_page=filtros.por_pagina, error_out=False)
    seguidos = ids_seguidos(usuario)
    return {
        "itens": [p.to_dict(p.id in seguidos) for p in paginacao.items],
        "pagina": paginacao.page,
        "total_paginas": paginacao.pages,
        "total": paginacao.total,
    }


def buscar(termo, usuario):
    seguidos = ids_seguidos(usuario)

    parlamentares = db.session.scalars(
        select(Parlamentar)
        .where(Parlamentar.nome.icontains(termo, autoescape=True))
        .order_by(Parlamentar.nome)
        .limit(LIMITE_BUSCA)
    )
    projetos = db.session.execute(
        select(ProjetoLei, Agenda.data)
        .join(Agenda, ProjetoLei.agenda_id == Agenda.id)
        .where(
            ProjetoLei.codigo_pl.icontains(termo, autoescape=True) | ProjetoLei.titulo.icontains(termo, autoescape=True)
        )
        .order_by(Agenda.data.desc())
        .limit(LIMITE_BUSCA)
    )
    votacoes = db.session.scalars(
        select(Votacao)
        .where(Votacao.objeto.icontains(termo, autoescape=True) | Votacao.descricao.icontains(termo, autoescape=True))
        .order_by(Votacao.data.desc())
        .limit(LIMITE_BUSCA)
    )
    dias_especiais = db.session.scalars(
        select(DiaEspecial)
        .join(Agenda, DiaEspecial.agenda_id == Agenda.id)
        .where(DiaEspecial.nome.icontains(termo, autoescape=True))
        .order_by(Agenda.data.desc())
        .limit(LIMITE_BUSCA)
    )

    return {
        "parlamentares": [p.to_dict(p.id in seguidos) for p in parlamentares],
        "projetos": [{**p.to_dict(), "data": data.isoformat()} for p, data in projetos],
        "votacoes": [v.to_dict() for v in votacoes],
        "dias_especiais": [d.to_dict() for d in dias_especiais],
    }


def listar_seguidos(usuario):
    return [s.parlamentar.to_dict(True) for s in usuario.parlamentares_seguidos]


def seguir_parlamentar(usuario, parlamentar_id):
    parlamentar = db.get_or_404(Parlamentar, parlamentar_id)
    db.session.add(UsuarioParlamentar(usuario_id=usuario.id, parlamentar_id=parlamentar.id))
    try:
        db.session.commit()
    except IntegrityError as erro:
        db.session.rollback()
        raise ErroApi("Você já segue este parlamentar.", 409) from erro
    return parlamentar


def deixar_de_seguir(usuario, parlamentar_id):
    seguimento = db.session.scalar(
        select(UsuarioParlamentar).where(
            UsuarioParlamentar.usuario_id == usuario.id,
            UsuarioParlamentar.parlamentar_id == parlamentar_id,
        )
    )
    if seguimento is None:
        raise ErroApi("Você não segue este parlamentar.", 404)
    db.session.delete(seguimento)
    db.session.commit()


def importar_parlamentares():
    existentes = {p.id_original: p for p in db.session.scalars(select(Parlamentar).where(Parlamentar.casa == "Câmara"))}
    criados = atualizados = 0
    for dep in integracoes.listar_deputados():
        parlamentar = existentes.get(dep["id"])
        if parlamentar is None:
            parlamentar = Parlamentar(id_original=dep["id"])
            db.session.add(parlamentar)
            criados += 1
        else:
            atualizados += 1
        parlamentar.nome = dep["nome"]
        parlamentar.partido = dep["siglaPartido"]
        parlamentar.estado = dep["siglaUf"]
        parlamentar.foto_link = dep.get("urlFoto")
    db.session.commit()
    logger.info("Parlamentares importados: %s novos, %s atualizados", criados, atualizados)
    return criados, atualizados


def importar_senadores():
    return senado.importar_senadores()


def detalhar_votacao(votacao, usuario):
    return votos.detalhar_votacao(votacao, ids_seguidos(usuario))


def detalhar_parlamentar(parlamentar, usuario):
    hoje = date.today()
    try:
        sincronizar_votacoes(hoje - timedelta(days=DIAS_HISTORICO), hoje)
    except ErroServicoExterno:
        logger.warning("Votações indisponíveis para o perfil de %s", parlamentar.nome)
    return votos.perfil_parlamentar(parlamentar, parlamentar.id in ids_seguidos(usuario))
