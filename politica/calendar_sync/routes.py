from flask import Blueprint, jsonify, request
from politica.auth.models import Usuario
from politica.legislation.models import ProjetoLei
from politica.calendar_sync.services import adicionar_evento_google_calendar

calendar_bp = Blueprint("calendar_sync", __name__)

@calendar_bp.post("/sincronizar/<int:usuario_id>/projeto/<int:projeto_id>")
def sincronizar_projeto_agenda(usuario_id, projeto_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    projeto = ProjetoLei.query.get_or_404(projeto_id)
    
    if not usuario.access_token:
        return jsonify({"error": "Usuário não possui token de acesso ao Google Calendar."}), 401
    
    # Usa a data do projeto ou a data atual se não houver
    data_str = projeto.agenda.date.strftime("%Y-%m-%d") if projeto.agenda else "2026-11-06"
    descricao = f"{projeto.resumo or 'Sem resumo'}\n\nStatus: {projeto.status}"
    
    resultado = adicionar_evento_google_calendar(
        access_token=usuario.access_token,
        titulo=projeto.codigo_pl,
        data_evento=data_str,
        descricao=descricao
    )
    
    if resultado["sucesso"]:
        return jsonify({"message": "Evento sincronizado com o Google Calendar com sucesso!"})
    
    return jsonify({"error": resultado["erro"]}), 500