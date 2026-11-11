from flask import Blueprint, jsonify, request, session

from politica.auth.decorators import login_required
from politica.auth.schemas import LoginIn, RegistroIn
from politica.auth.services import autenticar_usuario, registrar_usuario
from politica.validacao import validar

auth_bp = Blueprint("auth", __name__)


def iniciar_sessao(usuario):
    session.clear()
    session["usuario_id"] = usuario.id


@auth_bp.post("/registro")
def registro():
    dados = validar(RegistroIn, request.get_json(silent=True))
    usuario = registrar_usuario(dados.nome, dados.email, dados.senha)
    iniciar_sessao(usuario)
    return jsonify({"usuario": usuario.to_dict()}), 201


@auth_bp.post("/login")
def login():
    dados = validar(LoginIn, request.get_json(silent=True))
    usuario = autenticar_usuario(dados.email, dados.senha)
    iniciar_sessao(usuario)
    return jsonify({"usuario": usuario.to_dict()})


@auth_bp.post("/logout")
def logout():
    session.clear()
    return "", 204


@auth_bp.get("/me")
@login_required
def me(usuario):
    return jsonify({"usuario": usuario.to_dict()})
