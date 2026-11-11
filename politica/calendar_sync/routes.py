from flask import Blueprint, Response

from politica.auth.decorators import login_required
from politica.calendar_sync.services import gerar_ics
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
