from flask import Blueprint, Response, jsonify

from politica.auth.decorators import login_required
from politica.calendar_sync.services import criar_evento_google, gerar_ics
from politica.extensions import db
from politica.legislation.models import ProjetoLei

calendar_bp = Blueprint("calendar_sync", __name__)


@calendar_bp.get("/projetos/<int:projeto_id>.ics")
@login_required
def exportar_projeto(usuario, projeto_id):
    projeto = db.get_or_404(ProjetoLei, projeto_id)
    return Response(
        gerar_ics(projeto),
        mimetype="text/calendar",
        headers={"Content-Disposition": f'attachment; filename="projeto-{projeto.id}.ics"'},
    )


@calendar_bp.post("/projetos/<int:projeto_id>/google")
@login_required
def adicionar_ao_google(usuario, projeto_id):
    projeto = db.get_or_404(ProjetoLei, projeto_id)
    return jsonify({"link": criar_evento_google(usuario, projeto)}), 201
