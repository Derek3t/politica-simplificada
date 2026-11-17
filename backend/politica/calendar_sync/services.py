import logging
from datetime import datetime, timedelta, timezone

import requests
from flask import current_app

from politica.errors import ErroApi, ErroServicoExterno

logger = logging.getLogger(__name__)


def escapar(texto):
    return texto.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\r", "").replace("\n", "\\n")


def gerar_ics(projeto):
    data = projeto.agenda.data
    descricao = projeto.resumo or projeto.titulo
    linhas = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Politica Simplificada//PT-BR",
        "BEGIN:VEVENT",
        f"UID:projeto-{projeto.id}@politica-simplificada",
        f"DTSTAMP:{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        f"DTSTART;VALUE=DATE:{data.strftime('%Y%m%d')}",
        f"DTEND;VALUE=DATE:{(data + timedelta(days=1)).strftime('%Y%m%d')}",
        f"SUMMARY:{escapar('Votação ' + projeto.codigo_pl)}",
        f"DESCRIPTION:{escapar(descricao)}",
        "END:VEVENT",
        "END:VCALENDAR",
    ]
    return "\r\n".join(linhas) + "\r\n"


def obter_access_token(refresh_token):
    try:
        resposta = requests.post(
            current_app.config["GOOGLE_TOKEN_URL"],
            data={
                "client_id": current_app.config["GOOGLE_CLIENT_ID"],
                "client_secret": current_app.config["GOOGLE_CLIENT_SECRET"],
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            },
            timeout=current_app.config["HTTP_TIMEOUT"],
        )
    except requests.RequestException as erro:
        logger.warning("Falha ao renovar o token do Google: %s", erro)
        raise ErroServicoExterno("Google indisponível no momento.") from erro

    if resposta.status_code in (400, 401):
        raise ErroApi("Autorização do Google expirada. Entre com o Google novamente.", 403)
    if not resposta.ok:
        raise ErroServicoExterno("Google indisponível no momento.")
    return resposta.json()["access_token"]


def criar_evento_google(usuario, projeto):
    if not usuario.google_refresh_token:
        raise ErroApi("Entre com o Google para adicionar ao Google Calendar.", 403)

    data = projeto.agenda.data
    evento = {
        "summary": f"Votação {projeto.codigo_pl}",
        "description": projeto.resumo or projeto.titulo,
        "start": {"date": data.isoformat()},
        "end": {"date": (data + timedelta(days=1)).isoformat()},
    }
    access_token = obter_access_token(usuario.google_refresh_token)
    try:
        resposta = requests.post(
            current_app.config["GOOGLE_CALENDAR_URL"],
            json=evento,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=current_app.config["HTTP_TIMEOUT"],
        )
    except requests.RequestException as erro:
        logger.warning("Falha ao criar evento no Google Calendar: %s", erro)
        raise ErroServicoExterno("Google Calendar indisponível no momento.") from erro

    if resposta.status_code == 403:
        raise ErroApi("Sem permissão para escrever na sua agenda. Entre com o Google novamente.", 403)
    if not resposta.ok:
        logger.warning("Google Calendar respondeu %s: %s", resposta.status_code, resposta.text)
        raise ErroServicoExterno("Não foi possível criar o evento no Google Calendar.")
    return resposta.json().get("htmlLink")
