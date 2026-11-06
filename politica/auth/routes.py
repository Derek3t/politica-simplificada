from flask import Blueprint, jsonify, request, redirect
from politica.ext.db import db
from politica.auth.models import Usuario

auth_bp = Blueprint("auth", __name__)

@auth_bp.post("/callback")
def google_callback():
    data = request.json

    usuario = autenticar_usuario(data)

    return jsonify({
        "message": "Autenticado com sucesso",
        "usuario_id": usuario.id
    })