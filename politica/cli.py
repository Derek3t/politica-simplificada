from datetime import date

import click

from politica.errors import ErroApi


def registrar_comandos(app):
    @app.cli.command("importar-parlamentares")
    def importar_parlamentares():
        from politica.legislation.services import importar_parlamentares as importar

        try:
            criados, atualizados = importar()
        except ErroApi as erro:
            raise click.ClickException(erro.mensagem) from erro
        click.echo(f"{criados} parlamentares criados, {atualizados} atualizados.")

    @app.cli.command("sincronizar-agenda")
    @click.argument("data", type=click.DateTime(formats=["%Y-%m-%d"]), default=date.today().isoformat())
    def sincronizar_agenda(data):
        from politica.legislation.services import obter_ou_criar_agenda

        try:
            agenda = obter_ou_criar_agenda(data.date())
        except ErroApi as erro:
            raise click.ClickException(erro.mensagem) from erro
        click.echo(f"Agenda de {agenda.data}: {len(agenda.projetos_lei)} projetos.")
