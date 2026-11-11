from politica.ext.db import db
from politica.auth.models import Usuario
from politica.legislation.models import Agenda, ProjetoLei, Historico

def autenticar_usuario(data):
    usuario = Usuario.query.filter_by(
        email=data.get("email")
    ).first()

    if not usuario:
        usuario = Usuario(
            google_id=data["google_id"],
            email=data["email"],
            name=data["name"],
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token")
        )
        db.session.add(usuario)
    else:
        usuario.access_token = data["access_token"]

        if data.get("refresh_token"):
            usuario.refresh_token = data["refresh_token"]

    db.session.commit()

    return usuario
