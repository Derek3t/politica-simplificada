from datetime import datetime, timedelta, timezone


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
