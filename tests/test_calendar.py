from datetime import date

from politica.extensions import db
from politica.legislation.models import Agenda, ProjetoLei


def criar_projeto():
    agenda = Agenda(data=date(2026, 11, 11))
    agenda.projetos_lei.append(ProjetoLei(codigo_pl="PL 1/2026", titulo="Ementa; com, pontuação", resumo="Linha 1\nLinha 2"))
    db.session.add(agenda)
    db.session.commit()
    return agenda.projetos_lei[0]


def test_exportar_exige_login(client, app):
    projeto = criar_projeto()

    assert client.get(f"/api/calendar/projetos/{projeto.id}.ics").status_code == 401


def test_exportar_gera_ics_valido(usuario_logado, app):
    projeto = criar_projeto()

    resposta = usuario_logado.get(f"/api/calendar/projetos/{projeto.id}.ics")
    corpo = resposta.get_data(as_text=True)

    assert resposta.mimetype == "text/calendar"
    assert "DTSTART;VALUE=DATE:20261111" in corpo
    assert "DTEND;VALUE=DATE:20261112" in corpo
    assert "SUMMARY:Votação PL 1/2026" in corpo
    assert "DESCRIPTION:Linha 1\\nLinha 2" in corpo
    assert corpo.endswith("END:VCALENDAR\r\n")


def test_exportar_projeto_inexistente_retorna_404(usuario_logado):
    assert usuario_logado.get("/api/calendar/projetos/999.ics").status_code == 404
