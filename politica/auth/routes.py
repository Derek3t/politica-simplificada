from flask import Blueprint, jsonify, request, redirect
from politica.ext.db import db
from politica.auth.models import Usuario

auth_bp = Blueprint("auth", __name__)

@auth_bp.get("/login")
def google_login():
    # Aqui você redirecionaria para a URL de autenticação do Google OAuth 2.0
    # Exemplo simplificado de endpoint de recepção de dados pós-login:
    return jsonify({"message": "Redirecionar para o Google OAuth"})

@auth_bp.post("/callback")
def google_callback():
    data = request.json
    
    # Verifica se o usuário já existe pelo google_id ou email
    usuario = Usuario.query.filter_by(email=data.get("email")).first()
    
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
        # Atualiza os tokens caso já exista
        usuario.access_token = data["access_token"]
        if data.get("refresh_token"):
            usuario.refresh_token = data["refresh_token"]
            
    db.session.commit()
    return jsonify({"message": "Autenticado com sucesso", "usuario_id": usuario.id})