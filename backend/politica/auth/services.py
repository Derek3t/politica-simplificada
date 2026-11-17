from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from politica.auth.models import Usuario
from politica.errors import ErroApi
from politica.extensions import db


def buscar_por_email(email):
    return db.session.scalar(select(Usuario).where(Usuario.email == email.lower()))


def registrar_usuario(nome, email, senha):
    if buscar_por_email(email):
        raise ErroApi("Já existe uma conta com este e-mail.", 409)

    usuario = Usuario(nome=nome, email=email.lower(), senha_hash=generate_password_hash(senha))
    db.session.add(usuario)
    try:
        db.session.commit()
    except IntegrityError as erro:
        db.session.rollback()
        raise ErroApi("Já existe uma conta com este e-mail.", 409) from erro
    return usuario


def autenticar_usuario(email, senha):
    usuario = buscar_por_email(email)
    if not usuario or not usuario.senha_hash or not check_password_hash(usuario.senha_hash, senha):
        raise ErroApi("E-mail ou senha incorretos.", 401)
    return usuario


def entrar_com_google(perfil, refresh_token):
    if not perfil.get("email") or not perfil.get("email_verified"):
        raise ErroApi("Sua conta Google precisa ter um e-mail verificado.", 403)

    usuario = db.session.scalar(select(Usuario).where(Usuario.google_id == perfil["sub"]))
    if usuario is None:
        usuario = buscar_por_email(perfil["email"])
    if usuario is None:
        usuario = Usuario(nome=perfil.get("name") or perfil["email"], email=perfil["email"].lower())
        db.session.add(usuario)

    usuario.google_id = perfil["sub"]
    if refresh_token:
        usuario.google_refresh_token = refresh_token
    db.session.commit()
    return usuario
