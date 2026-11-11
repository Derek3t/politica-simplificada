from flask import Blueprint, jsonify, request
from politica.ext.db import db
from politica.auth.models import Usuario
from politica.legislation.models import ProjetoLei
from politica.legislation.services import gerar_resumo_projeto_lei, obter_ou_criar_agenda_por_data

legislation_bp = Blueprint("legislation", __name__)

@legislation_bp.post("/projetos/<int:projeto_id>/analisar")
def analisar_projeto(projeto_id):
    projeto = ProjetoLei.query.get_or_404(projeto_id)
    
    # Agora a função retorna a string diretamente
    resumo_ia = gerar_resumo_projeto_lei(projeto.titulo)
    
    if "Erro ao gerar resumo" in resumo_ia or "não configurada" in resumo_ia:
        return jsonify({"error": resumo_ia}), 500
        
    projeto.resumo = resumo_ia
    db.session.commit()
    
    return jsonify({"message": "Resumo gerado com sucesso", "resumo": projeto.resumo})

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
    
@legislation_bp.get("/agenda")
def obter_agenda_dia():
    data_str = request.args.get("data") # Ex: /api/legislation/agenda?data=2026-11-10
    usuario_id = request.args.get("usuario_id", type=int)
    
    if not data_str:
        return jsonify({"error": "O parâmetro 'data' (YYYY-MM-DD) é obrigatório."}), 400
        
    try:
        # 1. Lazy loading: garante que o dia existe no banco (popula se for a primeira vez)
        agenda = obter_ou_criar_agenda_por_data(data_str)
    except Exception as e:
        return jsonify({"error": f"Erro ao processar agenda: {str(e)}"}), 500
        
    # 2. Aplica a filtragem visual baseada nos parlamentares seguidos
    projetos_filtrados = filtrar_projetos_por_usuario(agenda, usuario_id)

    dias_especiais_serializados = [{"nome": d.nome, "tipo": d.tipo} for d in agenda.dias_especiais]

    return jsonify({
        "id": agenda.id,
        "data": agenda.date.strftime("%Y-%m-%d"),
        "resumo_geral": agenda.resumo,
        "feriados_e_civis": dias_especiais_serializados,
        "projetos_lei": projetos_filtrados
    })