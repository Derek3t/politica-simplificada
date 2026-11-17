import logging
from collections import Counter

from sqlalchemy import func, select

from politica.errors import ErroServicoExterno
from politica.extensions import db
from politica.legislation import integracoes
from politica.legislation.models import Historico, Parlamentar, ProjetoLei, Votacao, VotoParlamentar

logger = logging.getLogger(__name__)

LIMITE_VOTACOES_PERFIL = 60
LIMITE_VOTOS_NO_PERFIL = 30


def garantir_votos(votacoes):
    """Baixa os votos nominais da Câmara que ainda não estão no banco. Votação simbólica não tem votos."""
    pendentes = [v for v in votacoes if v.casa == "Câmara" and not v.votos_carregados]
    if not pendentes:
        return

    recebidos = integracoes.votos_de_votacoes([v.id_original for v in pendentes])
    deputados = dict(
        db.session.execute(select(Parlamentar.id_original, Parlamentar.id).where(Parlamentar.casa == "Câmara")).all()
    )
    for votacao in pendentes:
        votos = recebidos[votacao.id_original]
        if votos is None:
            continue
        for voto in votos:
            if voto["id_deputado"] in deputados:
                votacao.votos.append(VotoParlamentar(parlamentar_id=deputados[voto["id_deputado"]], voto=voto["voto"]))
        votacao.votos_carregados = True
    db.session.commit()


def tentar_garantir_votos(votacoes):
    try:
        garantir_votos(votacoes)
    except ErroServicoExterno:
        logger.warning("Votos nominais indisponíveis no momento")


def votacoes_recentes(casa, limite=LIMITE_VOTACOES_PERFIL):
    consulta = (
        select(Votacao).where(Votacao.casa == casa).order_by(Votacao.data.desc(), Votacao.id.desc()).limit(limite)
    )
    return db.session.scalars(consulta).all()


def contar_votos(consulta):
    return dict(Counter(dict(db.session.execute(consulta).all())).most_common())


def detalhar_votacao(votacao, seguidos):
    tentar_garantir_votos([votacao])

    placar = contar_votos(
        select(VotoParlamentar.voto, func.count())
        .where(VotoParlamentar.votacao_id == votacao.id)
        .group_by(VotoParlamentar.voto)
    )
    votos_seguidos = db.session.execute(
        select(Parlamentar, VotoParlamentar.voto)
        .join(VotoParlamentar, VotoParlamentar.parlamentar_id == Parlamentar.id)
        .where(VotoParlamentar.votacao_id == votacao.id, Parlamentar.id.in_(seguidos))
        .order_by(Parlamentar.nome)
    ).all()

    return {
        **votacao.to_dict(),
        "nominal": bool(placar),
        "placar": placar,
        "votos_seguidos": [{**p.to_dict(True), "voto": voto} for p, voto in votos_seguidos],
    }


def perfil_parlamentar(parlamentar, seguido):
    tentar_garantir_votos(votacoes_recentes(parlamentar.casa))

    votos = db.session.execute(
        select(Votacao, VotoParlamentar.voto)
        .join(VotoParlamentar, VotoParlamentar.votacao_id == Votacao.id)
        .where(VotoParlamentar.parlamentar_id == parlamentar.id)
        .order_by(Votacao.data.desc(), Votacao.id.desc())
        .limit(LIMITE_VOTOS_NO_PERFIL)
    ).all()
    resumo = contar_votos(
        select(VotoParlamentar.voto, func.count())
        .where(VotoParlamentar.parlamentar_id == parlamentar.id)
        .group_by(VotoParlamentar.voto)
    )
    autorias = db.session.scalars(
        select(ProjetoLei)
        .join(Historico, Historico.projeto_id == ProjetoLei.id)
        .where(Historico.parlamentar_id == parlamentar.id)
        .order_by(ProjetoLei.data_votacao.desc())
    ).all()

    return {
        **parlamentar.to_dict(seguido),
        "resumo_votos": resumo,
        "votos": [{**v.to_dict(), "voto": voto} for v, voto in votos],
        "autorias": [
            {
                "id": p.id,
                "codigo_pl": p.codigo_pl,
                "titulo": p.titulo,
                "data": p.data_votacao.isoformat() if p.data_votacao else None,
            }
            for p in autorias
        ],
    }
