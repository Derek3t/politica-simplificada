import logging
from datetime import date

from sqlalchemy import select

from politica.extensions import db
from politica.legislation import integracoes
from politica.legislation.models import Parlamentar, Votacao, VotoParlamentar

logger = logging.getLogger(__name__)

CASA = "Senado"
RESULTADOS = {"A": True, "R": False}
VOTOS = {
    "P-NRV": "Presente, sem voto",
    "AP": "Ausente",
    "MIS": "Ausente",
    "LS": "Ausente",
    "NCom": "Ausente",
    "Presidente (art. 51 RISF)": "Presidente",
}


def importar_senadores():
    existentes = {p.id_original: p for p in db.session.scalars(select(Parlamentar).where(Parlamentar.casa == CASA))}
    criados = atualizados = 0
    for sen in integracoes.listar_senadores():
        parlamentar = existentes.get(sen["id"])
        if parlamentar is None:
            parlamentar = Parlamentar(id_original=sen["id"], casa=CASA)
            db.session.add(parlamentar)
            criados += 1
        else:
            atualizados += 1
        parlamentar.nome = sen["nome"]
        parlamentar.partido = sen["siglaPartido"]
        parlamentar.estado = sen["siglaUf"]
        parlamentar.foto_link = sen.get("urlFoto")
    db.session.commit()
    logger.info("Senadores importados: %s novos, %s atualizados", criados, atualizados)
    return criados, atualizados


def atualizar_votacao(votacao, dados):
    votacao.casa = CASA
    votacao.data = date.fromisoformat(dados["dataSessao"])
    votacao.objeto = dados.get("identificacao")
    votacao.descricao = dados.get("descricaoVotacao") or dados.get("ementa") or "Sem descrição"
    votacao.aprovada = RESULTADOS.get(dados.get("resultadoVotacao"))


def registrar_votos(votacao, dados, senadores):
    for voto in dados.get("votos") or []:
        senador_id = senadores.get(voto["codigoParlamentar"])
        if senador_id is not None:
            sigla = voto.get("siglaVotoParlamentar") or voto.get("descricaoVotoParlamentar") or "Sem registro"
            votacao.votos.append(VotoParlamentar(parlamentar_id=senador_id, voto=VOTOS.get(sigla, sigla)))
    votacao.votos_carregados = True


def sincronizar_votacoes_senado(inicio, fim, tipos):
    """Votações nominais do Plenário do Senado de projetos (PEC, PLP, PL...), com o voto de cada senador."""
    recebidas = [v for v in integracoes.votacoes_senado(inicio, fim) if v.get("sigla") in tipos]
    senadores = dict(
        db.session.execute(select(Parlamentar.id_original, Parlamentar.id).where(Parlamentar.casa == CASA)).all()
    )
    existentes = {
        v.id_original: v
        for v in db.session.scalars(select(Votacao).where(Votacao.casa == CASA, Votacao.data.between(inicio, fim)))
    }
    for dados in recebidas:
        id_original = f"SF-{dados['codigoSessaoVotacao']}"
        votacao = existentes.get(id_original)
        if votacao is None:
            votacao = Votacao(id_original=id_original)
            db.session.add(votacao)
        atualizar_votacao(votacao, dados)
        if senadores and not votacao.votos_carregados:
            registrar_votos(votacao, dados, senadores)
    db.session.commit()
