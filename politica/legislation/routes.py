from flask import Blueprint, jsonify, request
from politica.ext.db import db
from politica.legislation.models import ProjetoLei
from politica.legislation.services import gerar_resumo_projeto_lei

legislation_bp = Blueprint("legislation", __name__)

@legislation_bp.post("/projetos/<int:projeto_id>/analisar")
def analisar_projeto(projeto_id):
    projeto = ProjetoLei.query.get_or_404(projeto_id)
    
    # Exemplo enviando o título ou texto base para a IA
    resultado = gerar_resumo_projeto_lei(projeto.titulo)
    
    if resultado["sucesso"]:
        projeto.resumo = resultado["analise_ia"]
        db.session.commit()
        return jsonify({"message": "Resumo gerado com sucesso", "resumo": projeto.resumo})
    
    return jsonify({"error": resultado.get("erro")}), 500

@legislation_bp.get("/agenda/<int:usuario_id>")
def obter_feed_agenda(usuario_id):
    resultado = buscar_agenda_usuario(usuario_id)
    # Serializa os dados da agenda (com seus projetos e dias especiais) para JSON
    return jsonify(resultado)

@legislation_bp.post("/parlamentares/<int:parlamentar_id>/seguir")
def rota_seguir_parlamentar(parlamentar_id):
    # Aqui você obtém o id do usuário logado (ex: via token JWT, session do Flask ou request.json)
    # Exemplo simulado recebendo via JSON ou header de autenticação:
    dados = request.get_json() or {}
    usuario_id = dados.get("usuario_id") # Ou extraído do seu decorador de autenticação OAuth
    
    if not usuario_id:
        return jsonify({"error": "Usuário não autenticado."}), 401
        
    resultado, status_code = seguir_parlamentar(usuario_id, parlamentar_id)
    
    if not resultado["sucesso"]:
        return jsonify({"error": resultado["erro"]}), status_code
        
    return jsonify(resultado), 200