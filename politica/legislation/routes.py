from flask import Blueprint, jsonify, request

from politica.auth.decorators import login_required, usuario_atual
from politica.extensions import db
from politica.legislation import services
from politica.legislation.models import DiaEspecial, Parlamentar, ProjetoLei
from politica.legislation.schemas import AgendaQuery, ParlamentaresQuery
from politica.validacao import validar

legislation_bp = Blueprint("legislation", __name__)


@legislation_bp.get("/agenda")
def agenda_do_dia():
    filtros = validar(AgendaQuery, request.args.to_dict())
    agenda = services.obter_ou_criar_agenda(filtros.data)
    return jsonify(services.montar_agenda(agenda, usuario_atual(), filtros.apenas_seguidos, filtros.incluir_comissoes))


@legislation_bp.get("/projetos/<int:projeto_id>")
def detalhe_projeto(projeto_id):
    projeto = db.get_or_404(ProjetoLei, projeto_id)
    return jsonify(services.detalhar_projeto(projeto, usuario_atual()))


@legislation_bp.post("/projetos/<int:projeto_id>/analisar")
@login_required
def analisar_projeto(usuario, projeto_id):
    projeto = db.get_or_404(ProjetoLei, projeto_id)
    services.analisar_projeto(projeto)
    return jsonify(services.detalhar_projeto(projeto, usuario))


@legislation_bp.post("/dias-especiais/<int:dia_id>/contextualizar")
@login_required
def contextualizar_dia(usuario, dia_id):
    dia = db.get_or_404(DiaEspecial, dia_id)
    return jsonify(services.contextualizar_dia_especial(dia).to_dict())


@legislation_bp.get("/parlamentares")
def parlamentares():
    filtros = validar(ParlamentaresQuery, request.args.to_dict())
    return jsonify(services.listar_parlamentares(filtros, usuario_atual()))


@legislation_bp.get("/parlamentares/seguidos")
@login_required
def parlamentares_seguidos(usuario):
    return jsonify({"itens": services.listar_seguidos(usuario)})


@legislation_bp.post("/parlamentares/<int:parlamentar_id>/seguir")
@login_required
def seguir(usuario, parlamentar_id):
    parlamentar = services.seguir_parlamentar(usuario, parlamentar_id)
    return jsonify(parlamentar.to_dict(True)), 201


@legislation_bp.delete("/parlamentares/<int:parlamentar_id>/seguir")
@login_required
def deixar_de_seguir(usuario, parlamentar_id):
    db.get_or_404(Parlamentar, parlamentar_id)
    services.deixar_de_seguir(usuario, parlamentar_id)
    return "", 204
