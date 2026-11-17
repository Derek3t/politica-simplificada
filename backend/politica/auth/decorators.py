from functools import wraps

from flask import session

from politica.auth.models import Usuario
from politica.errors import ErroApi
from politica.extensions import db


def usuario_atual():
    usuario_id = session.get("usuario_id")
    return db.session.get(Usuario, usuario_id) if usuario_id else None


def login_required(funcao):
    @wraps(funcao)
    def interna(*args, **kwargs):
        usuario = usuario_atual()
        if usuario is None:
            raise ErroApi("Faça login para continuar.", 401)
        return funcao(usuario, *args, **kwargs)

    return interna
