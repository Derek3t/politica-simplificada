import logging
from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from politica.auth.models import UsuarioParlamentar
from politica.errors import ErroApi, ErroServicoExterno
from politica.extensions import db
from politica.legislation import integracoes
from politica.legislation.models import Agenda, DiaEspecial, Historico, Parlamentar, ProjetoLei

logger = logging.getLogger(__name__)

SIGLA_PLENARIO = "PLEN"
TIPOS_RELEVANTES = {"PL", "PLP", "PEC", "PDL", "MPV", "PLN", "PLV"}


def eh_deliberativo(evento):
    tipo = evento.get("descricaoTipo", "").lower()
    cancelado = evento.get("situacao", "").lower().startswith("cancelad")
    return "deliberativ" in tipo and "não deliberativ" not in tipo and not cancelado


def carregar_feriados(agenda):
    try:
        feriados = integracoes.feriados_do_ano(agenda.data.year)
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
        select(Parlamentar.id_original, Parlamentar.id).where(Parlamentar.id_original.in_(ids_deputados))
    ).all()
    mapa = dict(parlamentares)

    for projeto in projetos:
        for id_deputado in autores[int(projeto.id_original)]:
            if id_deputado in mapa:
                projeto.historicos.append(Historico(parlamentar_id=mapa[id_deputado], posicionamento="Autor"))


def criar_projeto(proposicao, item, evento, data):
    sigla = proposicao.get("siglaTipo")
    return ProjetoLei(
        id_original=str(proposicao["id"]),
        tipo=sigla,
        codigo_pl=f"{sigla} {proposicao.get('numero')}/{proposicao.get('ano')}",
        titulo=proposicao.get("ementa") or item.get("topico") or "Sem ementa",
        orgao=(evento.get("orgaos") or [{}])[0].get("nome"),
        horario=horario_do_evento(evento),
        status=item.get("situacaoItem") or "Em pauta",
        data_votacao=data,
    )


def carregar_pauta(agenda):
    eventos = [e for e in integracoes.eventos_do_dia(agenda.data) if eh_deliberativo(e)]
    pautas = integracoes.pautas_dos_eventos([e["id"] for e in eventos])

    existentes = {p.id_original for p in agenda.projetos_lei}
    novos, do_plenario = [], []
    for evento, itens in zip(eventos, pautas):
        no_plenario = (evento.get("orgaos") or [{}])[0].get("sigla") == SIGLA_PLENARIO
        for item in itens:
            proposicao = item.get("proposicaoRelacionada_") or item.get("proposicao_")
            if not proposicao or proposicao.get("siglaTipo") not in TIPOS_RELEVANTES:
                continue
            if str(proposicao["id"]) in existentes:
                continue
            existentes.add(str(proposicao["id"]))
            projeto = criar_projeto(proposicao, item, evento, agenda.data)
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
    return agenda


def ids_seguidos(usuario):
    if usuario is None:
        return set()
    return {s.parlamentar_id for s in usuario.parlamentares_seguidos}


def montar_agenda(agenda, usuario, apenas_seguidos=False):
    seguidos = ids_seguidos(usuario)
    projetos = []
    for projeto in agenda.projetos_lei:
        destacado = any(h.parlamentar_id in seguidos for h in projeto.historicos)
        if apenas_seguidos and not destacado:
            continue
        projetos.append(projeto.to_dict(destacado))
    projetos.sort(key=lambda p: (not p["destacado"], p["horario"] or "99:99"))

    return {
        "id": agenda.id,
        "data": agenda.data.isoformat(),
        "dias_especiais": [d.to_dict() for d in agenda.dias_especiais],
        "projetos_lei": projetos,
    }


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
    analise = integracoes.analisar_com_gemini(projeto.titulo)
    for campo, valor in analise.items():
        setattr(projeto, campo, valor)
    db.session.commit()
    return projeto


def contextualizar_dia_especial(dia):
    if dia.contexto_historico:
        return dia
    contexto = integracoes.contextualizar_dia_especial(dia.nome, dia.agenda.data.strftime("%d/%m/%Y"))
    for campo, valor in contexto.items():
        setattr(dia, campo, valor)
    db.session.commit()
    return dia


def listar_parlamentares(filtros, usuario):
    consulta = select(Parlamentar).order_by(Parlamentar.nome)
    if filtros.busca:
        consulta = consulta.where(Parlamentar.nome.ilike(f"%{filtros.busca}%"))
    if filtros.estado:
        consulta = consulta.where(Parlamentar.estado == filtros.estado.upper())
    if filtros.partido:
        consulta = consulta.where(Parlamentar.partido.ilike(filtros.partido))

    paginacao = db.paginate(consulta, page=filtros.pagina, per_page=filtros.por_pagina, error_out=False)
    seguidos = ids_seguidos(usuario)
    return {
        "itens": [p.to_dict(p.id in seguidos) for p in paginacao.items],
        "pagina": paginacao.page,
        "total_paginas": paginacao.pages,
        "total": paginacao.total,
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
    existentes = {p.id_original: p for p in db.session.scalars(select(Parlamentar))}
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
