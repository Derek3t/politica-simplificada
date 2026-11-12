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

    @app.cli.command("precarregar")
    @click.option("--passados", type=click.IntRange(0, 60), default=7, show_default=True, help="Dias antes de hoje.")
    @click.option("--futuros", type=click.IntRange(0, 60), default=10, show_default=True, help="Dias depois de hoje.")
    @click.option("--forcar-parlamentares", is_flag=True, help="Reimporta os deputados mesmo se já existirem.")
    @click.option("--ia", "com_ia", is_flag=True, help="Gera resumos e contextos com o Gemini.")
    @click.option("--limite-ia", type=click.IntRange(0, 50), default=5, show_default=True, help="Máximo por tipo.")
    def precarregar_dados(passados, futuros, forcar_parlamentares, com_ia, limite_ia):
        from politica.precarga import precarregar

        relatorio = precarregar(
            passados=passados,
            futuros=futuros,
            forcar_parlamentares=forcar_parlamentares,
            com_ia=com_ia,
            limite_ia=limite_ia,
            avisar=click.echo,
        )
        click.echo(
            f"\nResumo: {relatorio.agendas_carregadas} agendas, {relatorio.projetos} projetos "
            f"({relatorio.projetos_plenario} no Plenário), {relatorio.dias_especiais} datas especiais, "
            f"{relatorio.votacoes} votações."
        )
        if relatorio.tem_falhas:
            raise click.ClickException("Algumas etapas falharam. Rode o comando de novo para completar.")
