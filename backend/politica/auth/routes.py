import logging

from authlib.integrations.base_client.errors import OAuthError
from flask import Blueprint, current_app, jsonify, redirect, request, session

from politica.auth.decorators import login_required
from politica.auth.schemas import LoginIn, RegistroIn
from politica.auth.services import autenticar_usuario, entrar_com_google, registrar_usuario
from politica.errors import ErroApi
from politica.extensions import oauth
from politica.validacao import validar

logger = logging.getLogger(__name__)

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


@auth_bp.get("/google/login")
def google_login():
    if not current_app.config["GOOGLE_CLIENT_ID"] or not current_app.config["GOOGLE_CLIENT_SECRET"]:
        raise ErroApi("Login com Google não configurado.", 503)
    return oauth.google.authorize_redirect(
        current_app.config["GOOGLE_REDIRECT_URI"], access_type="offline", prompt="consent"
    )


@auth_bp.get("/google/callback")
def google_callback():
    frontend = current_app.config["FRONTEND_URL"]
    try:
        token = oauth.google.authorize_access_token()
        usuario = entrar_com_google(token["userinfo"], token.get("refresh_token"))
    except (OAuthError, KeyError) as erro:
        logger.warning("Falha no login com Google: %s", erro)
        return redirect(f"{frontend}/login?erro=google")
    except ErroApi as erro:
        logger.warning("Login com Google recusado: %s", erro.mensagem)
        return redirect(f"{frontend}/login?erro=google")

    iniciar_sessao(usuario)
    return redirect(f"{frontend}/agenda")
