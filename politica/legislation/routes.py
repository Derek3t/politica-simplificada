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