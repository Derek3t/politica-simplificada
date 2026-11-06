import requests
from flask import current_app

def adicionar_evento_google_calendar(access_token: str, titulo: str, data_evento: str, descricao: str) -> dict:
    """
    Cria um evento de dia inteiro (ou horário específico) na agenda principal do usuário via Google Calendar API.
    """
    url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Configurando como um evento de dia inteiro baseado na data da agenda
    body = {
        "summary": f"🏛️ [Política Simplificada] {titulo}",
        "description": descricao,
        "start": {
            "date": data_evento  # Formato "YYYY-MM-DD"
        },
        "end": {
            "date": data_evento  # Formato "YYYY-MM-DD"
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=body)
        if response.status_code == 201:
            return {"sucesso": True, "dados": response.json()}
        else:
            return {"sucesso": False, "erro": response.json().get("error", {}).get("message", "Erro desconhecido")}
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}