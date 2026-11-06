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

def buscar_agenda_usuario(usuario_id: int):
    usuario = Usuario.query.get_or_404(usuario_id)
    
    # Extrai os IDs dos parlamentares seguidos pelo usuário
    parlamentares_ids = [p.parlamentar_id for p in usuario.parlamentares_seguidos]
    
    if not parlamentares_ids:
        # Comportamento 1: Agenda Global (completa)
        agendas = Agenda.query.order_by(Agenda.date.desc()).all()
        return {"tipo": "global", "dados": agendas}
    else:
        # Comportamento 2: Agenda Personalizada baseada nos parlamentares seguidos
        # Busca projetos ligados aos parlamentares que o usuário segue
        projetos = (
            db.session.query(ProjetoLei)
            .join(Historico, Historico.projeto_id == ProjetoLei.id)
            .filter(Historico.parlamentar_id.in_(parlamentares_ids))
            .all()
        )
        # Extrai as agendas referentes a esses projetos
        agendas_ids = [p.agenda_ref for p in projetos]
        agendas = Agenda.query.filter(Agenda.id.in_(agendas_ids)).order_by(Agenda.date.desc()).all()
        
        return {"tipo": "personalizada", "dados": agendas}