import ast
import re
import subprocess
import sys
from html import escape
from pathlib import Path

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name

RAIZ = Path(__file__).resolve().parent.parent
DOCS = Path(__file__).resolve().parent
sys.path.insert(0, str(DOCS))
sys.path.insert(0, str(RAIZ))

from diagramas import diagrama_arquitetura, diagrama_er

from politica import create_app
from politica.config import TestingConfig
from politica.extensions import db

INTEGRANTES = ["Derek da Penha Teixeira", "João Gabriel Bouzan Louzada", "Victor Machado Martins"]
GRUPO = "Grupo X"
FORMATADOR = HtmlFormatter(nowrap=True, style="friendly")


def fonte_da_definicao(caminho, nome):
    texto = (RAIZ / caminho).read_text()
    for no in ast.walk(ast.parse(texto)):
        if isinstance(no, ast.FunctionDef | ast.ClassDef) and no.name == nome:
            inicio = no.decorator_list[0].lineno if no.decorator_list else no.lineno
            return "\n".join(texto.splitlines()[inicio - 1 : no.end_lineno])
    raise LookupError(f"{nome} não encontrado em {caminho}")


def fonte_entre_marcas(caminho, inicio, fim):
    linhas = (RAIZ / caminho).read_text().splitlines()
    primeira = next(i for i, linha in enumerate(linhas) if inicio in linha)
    ultima = next(i for i, linha in enumerate(linhas) if i > primeira and fim in linha)
    return "\n".join(linhas[primeira:ultima])


def bloco_de_codigo(codigo, linguagem, legenda):
    lexer = get_lexer_by_name(linguagem)
    return (
        f'<figure class="codigo"><figcaption>{escape(legenda)}</figcaption>'
        f"<pre>{highlight(codigo, lexer, FORMATADOR)}</pre></figure>"
    )


def definicao(caminho, nome, linguagem="python"):
    return bloco_de_codigo(fonte_da_definicao(caminho, nome), linguagem, f"{caminho} - {nome}")


def executar(comando, cwd):
    return subprocess.run(comando, cwd=cwd, capture_output=True, text=True, check=False).stdout


def total_de_testes():
    saida_py = executar([str(RAIZ / "venv/bin/python"), "-m", "pytest", "-q"], RAIZ)
    saida_js = executar(["npx", "vitest", "run"], RAIZ / "frontend")
    backend = re.search(r"(\d+) passed", saida_py)
    frontend = re.search(r"Tests\s+(\d+) passed", saida_js)
    return int(backend.group(1)), int(frontend.group(1))


def total_de_linhas(padroes):
    total = 0
    for padrao in padroes:
        for arquivo in RAIZ.glob(padrao):
            if "node_modules" not in arquivo.parts and "dist" not in arquivo.parts:
                total += len(arquivo.read_text().splitlines())
    return total


def imagem(arquivo, legenda, largura="100%"):
    return f'<figure class="tela"><img src="img/{arquivo}" style="width:{largura}" alt="{escape(legenda)}"/><figcaption>{escape(legenda)}</figcaption></figure>'


CSS = """
@page { size: A4; margin: 20mm 18mm 20mm 18mm; }
* { box-sizing: border-box; }
body { font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; font-size: 10.5pt; line-height: 1.5; color: #1e293b; margin: 0; }
h1 { font-size: 19pt; color: #0c1b3d; border-bottom: 2px solid #2563eb; padding-bottom: 4px; margin: 0 0 12px; break-after: avoid; }
h2 { font-size: 13pt; color: #0c1b3d; margin: 20px 0 6px; break-after: avoid; }
h3 { font-size: 11pt; color: #1d4ed8; margin: 14px 0 4px; break-after: avoid; }
p { margin: 6px 0; text-align: justify; }
ul, ol { margin: 6px 0; padding-left: 20px; }
li { margin: 2px 0; }
section { margin-top: 26px; }
section.nova { break-before: page; margin-top: 0; }
code { font-family: Menlo, Consolas, monospace; font-size: 9pt; background: #f1f5f9; padding: 0 3px; border-radius: 3px; }
table { border-collapse: collapse; width: 100%; margin: 8px 0; font-size: 9.5pt; break-inside: auto; }
th { background: #0c1b3d; color: #fff; text-align: left; padding: 5px 7px; }
td { border-bottom: 1px solid #e2e8f0; padding: 5px 7px; vertical-align: top; }
tr { break-inside: avoid; }
figure { margin: 10px 0; }
figcaption { font-size: 9pt; color: #64748b; margin-bottom: 3px; }
figure.codigo { break-inside: avoid; }
figure.codigo figcaption { font-family: Menlo, Consolas, monospace; font-size: 8.5pt; background: #0c1b3d; color: #e2e8f0; padding: 3px 8px; border-radius: 4px 4px 0 0; margin: 0; }
pre { margin: 0; background: #f8fafc; border: 1px solid #e2e8f0; border-top: none; border-radius: 0 0 4px 4px; padding: 8px 10px; font-family: Menlo, Consolas, monospace; font-size: 7.8pt; line-height: 1.38; white-space: pre-wrap; word-break: break-word; }
figure.tela { break-inside: avoid; text-align: center; }
figure.tela img { border: 1px solid #cbd5e1; border-radius: 6px; }
figure.tela figcaption { margin: 4px 0 0; }
.capa { break-before: auto; height: 245mm; display: flex; flex-direction: column; justify-content: center; text-align: left; }
.capa .marca { font-size: 11pt; letter-spacing: 3px; color: #2563eb; text-transform: uppercase; font-weight: 700; }
.capa h1 { font-size: 34pt; border: none; margin: 8px 0 4px; line-height: 1.1; }
.capa .sub { font-size: 14pt; color: #475569; margin-bottom: 40px; }
.capa .grupo { font-size: 13pt; font-weight: 700; color: #0c1b3d; margin-bottom: 8px; }
.capa ul { list-style: none; padding: 0; font-size: 12pt; }
.capa .rodape { margin-top: 60px; color: #64748b; font-size: 10pt; }
.sumario { break-before: page; }
.sumario ol { font-size: 11pt; line-height: 1.9; padding-left: 30px; }
.aviso { background: #eff6ff; border-left: 4px solid #2563eb; padding: 8px 12px; margin: 10px 0; font-size: 10pt; }
.grade { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; align-items: start; }
.duas { display: grid; grid-template-columns: 1fr 1.5fr; gap: 12px; align-items: start; }
.diagrama { break-inside: avoid; margin: 10px 0; }
.diagrama svg { width: 92%; height: auto; display: block; margin: 0 auto; }
pre.bloco { break-inside: avoid; }
"""


def sumario():
    itens = [
        "Descrição geral e funcionalidades",
        "Telas do sistema",
        "Modelo de dados (diagrama ER)",
        "Arquitetura adotada",
        "Detalhamento técnico do código",
        "Tecnologias utilizadas e justificativas",
        "Atendimento aos critérios de avaliação",
        "Como executar o projeto",
        "Principais desafios e soluções",
        "Limitações e próximos passos",
    ]
    lista = "".join(f"<li>{item}</li>" for item in itens)
    return f'<div class="sumario"><h1>Sumário</h1><ol>{lista}</ol></div>'


def capa():
    nomes = "".join(f"<li>{nome}</li>" for nome in INTEGRANTES)
    return f"""
<div class="capa">
  <div class="marca">Documentação técnica</div>
  <h1>Política Simplificada</h1>
  <div class="sub">Plataforma de Guia Político</div>
  <div class="grupo">{GRUPO}</div>
  <ul>{nomes}</ul>
  <div class="rodape">UVV · Novembro de 2026</div>
</div>"""


def secao_descricao():
    return """
<section>
<h1>1. Descrição geral e funcionalidades</h1>
<p>A <b>Política Simplificada</b> é uma aplicação web que apresenta o que acontece no Congresso Brasileiro em formato de agenda diária, com linguagem simples. Ela consulta dados abertos da Câmara dos Deputados, cruza com feriados e datas cívicas e usa inteligência artificial para traduzir o “juridiquês” das proposições em resumos que um cidadão comum consegue entender.</p>
<h2>Público-alvo e proposta de valor</h2>
<p>Cidadãos brasileiros que querem acompanhar a política nacional, mas não têm tempo ou facilidade para ler a linguagem oficial do Congresso. A proposta é democratizar o acesso à informação por meio de uma navegação diária no estilo agenda, com resumos curtos, impacto prático e comparação com outros países.</p>
<h2>Funcionalidades implementadas</h2>
<table>
<tr><th style="width:27%">Funcionalidade</th><th>Descrição</th></tr>
<tr><td>Agenda diária</td><td>Linha do tempo com os projetos de lei na pauta do Plenário no dia escolhido, faixa de navegação entre dias e opção de incluir as comissões. Projetos de parlamentares seguidos aparecem em destaque.</td></tr>
<tr><td>Resumo por IA</td><td>Para cada projeto, o Gemini gera “o que significa”, impacto prático e panorama internacional. O resultado é salvo para não repetir a chamada.</td></tr>
<tr><td>Feriados e datas cívicas</td><td>Feriados nacionais vindos da Brasil API, com explicação do contexto histórico, da importância e do impacto legislativo da data.</td></tr>
<tr><td>Votações</td><td>Lista paginada das votações de mérito do Plenário (hoje, semana ou mês) com status Aprovado, Em andamento ou Rejeitado.</td></tr>
<tr><td>Calendário mensal</td><td>Grade do mês com marcadores de feriados e votações e resumo do dia selecionado.</td></tr>
<tr><td>Parlamentares</td><td>Lista dos 513 deputados com busca por nome, filtro por estado e opção de seguir ou deixar de seguir.</td></tr>
<tr><td>Busca global</td><td>Procura simultânea em parlamentares, projetos, votações e datas cívicas.</td></tr>
<tr><td>Conta de usuário</td><td>Cadastro e login por e-mail e senha, com sessão em cookie e validação dos dados no servidor.</td></tr>
<tr><td>Exportar para o calendário</td><td>Download de arquivo <code>.ics</code> com a data do projeto, compatível com Google Calendar, Outlook e Apple Calendário.</td></tr>
</table>
<div class="aviso">A proposta original previa login com OAuth 2.0 do Google e inserção direta de eventos na Google Calendar API. Para a demonstração adotamos login por e-mail e senha e exportação em <code>.ics</code>, que entrega o mesmo resultado ao usuário sem depender de credenciais no Google Cloud. A decisão está justificada na seção 6.</div>
</section>"""


def secao_telas():
    return f"""
<section>
<h1>2. Telas do sistema</h1>
<p>As capturas abaixo foram feitas na aplicação em execução, com dados reais da Câmara dos Deputados.</p>
<div class="grade">
{imagem("agenda.png", "Agenda diária: faixa de dias, filtro de comissões e linha do tempo.")}
{imagem("votacoes.png", "Votações da semana, com período, status e paginação.")}
{imagem("calendario.png", "Calendário mensal: feriados (verde) e votações (roxo).")}
{imagem("busca.png", "Busca global agrupada por tipo de resultado.")}
</div>
<div class="duas">
<figure class="tela"><img src="img/agenda-mobile.png" style="width:100%" alt="Agenda no celular"/><figcaption>Agenda em tela de 390 px, com menu inferior.</figcaption></figure>
<div>
{imagem("login.png", "Login, com validação no cliente e no servidor.")}
{imagem("parlamentares.png", "Parlamentares com busca e botão Seguir.")}
</div>
</div>
</section>"""


def secao_er(metadados):
    return f"""
<section class="nova">
<h1>3. Modelo de dados (diagrama ER)</h1>
<p>O banco é relacional (SQLite) e as tabelas são geradas a partir dos modelos do SQLAlchemy, versionadas com Alembic. O diagrama abaixo foi gerado automaticamente a partir dos metadados dos modelos, portanto reflete exatamente o código.</p>
<div class="diagrama">{diagrama_er(metadados)}</div>
<p><b>Legenda:</b> PK = chave primária, FK = chave estrangeira, UK = restrição de unicidade. “N” e “1” indicam a cardinalidade de cada relacionamento.</p>
<h2>Descrição das tabelas</h2>
<table>
<tr><th style="width:22%">Tabela</th><th>Papel</th></tr>
<tr><td><code>usuarios</code></td><td>Contas da plataforma. A senha é guardada apenas como hash; o e-mail é único.</td></tr>
<tr><td><code>parlamentar</code></td><td>Deputados importados da API da Câmara. <code>id_original</code> é o identificador da Câmara e é único, o que evita duplicar a importação.</td></tr>
<tr><td><code>usuario_parlamentar</code></td><td>Tabela associativa N:N entre usuários e parlamentares seguidos. A restrição única impede seguir duas vezes.</td></tr>
<tr><td><code>agenda</code></td><td>Um registro por dia consultado. Funciona como cache global: depois da primeira consulta o dia é servido do banco.</td></tr>
<tr><td><code>projetos_lei</code></td><td>Projetos na pauta de um dia, com o resumo, o impacto e a comparação internacional geradas pela IA. É único por agenda e projeto original.</td></tr>
<tr><td><code>historico</code></td><td>Tabela associativa N:N entre parlamentares e projetos, guardando o posicionamento (hoje, “Autor”).</td></tr>
<tr><td><code>dias_especiais</code></td><td>Feriados e datas cívicas de cada dia, com o contexto gerado pela IA.</td></tr>
<tr><td><code>votacoes</code></td><td>Votações de mérito do Plenário sincronizadas da Câmara. Não se relaciona com as demais porque os identificadores da Câmara para votações e pautas nem sempre se correspondem.</td></tr>
</table>
<h2>Decisões de modelagem</h2>
<ul>
<li>Integridade referencial ativada no SQLite (<code>PRAGMA foreign_keys=ON</code>) e <code>ON DELETE CASCADE</code> nas chaves estrangeiras, em sintonia com <code>cascade="all, delete-orphan"</code> nos relacionamentos.</li>
<li>Restrições de unicidade no banco, e não só na aplicação, para que uma corrida entre requisições não gere duplicatas.</li>
<li>Nomes de colunas padronizados em minúsculas e em português, no mesmo padrão dos modelos.</li>
</ul>
</section>"""


def secao_arquitetura():
    return f"""
<section>
<h1>4. Arquitetura adotada</h1>
<p>O projeto é uma aplicação em camadas com separação clara entre apresentação, regras de negócio, acesso a dados e integrações. O frontend é uma SPA em Vue que conversa com uma API JSON em Flask. Em desenvolvimento o Vite encaminha as chamadas <code>/api</code> para o Flask, o que evita CORS e permite usar cookie de sessão.</p>
<div class="diagrama">{diagrama_arquitetura()}</div>
<h2>Application Factory</h2>
<p>O Flask é criado em <code>create_app()</code> (<code>politica/__init__.py</code>), que recebe a classe de configuração. Isso permite criar uma aplicação para produção, outra para desenvolvimento e outra, com banco em memória, para os testes. A função registra as extensões, os blueprints, os handlers de erro e os comandos de linha de comando.</p>
<h2>Organização em módulos</h2>
<pre class="bloco" style="border-top:1px solid #e2e8f0;border-radius:4px">politica/
  __init__.py        create_app (application factory)
  config.py          Development / Production / Testing (variável APP_ENV)
  extensions.py      db, migrate, cors
  errors.py          exceções da API e handlers JSON
  validacao.py       validação de entrada com Pydantic
  cli.py             comandos flask importar-parlamentares / sincronizar-agenda
  auth/              blueprint: models, schemas, services, decorators, routes
  legislation/       blueprint: models, schemas, services, integracoes, routes
  calendar_sync/     blueprint: exportação .ics
migrations/          versões do Alembic
tests/               pytest
frontend/src/        api/, composables/, components/, views/, utils/, router.js</pre>
<p>Cada blueprint segue o mesmo padrão: <b>routes</b> recebem e validam a requisição e devolvem JSON; <b>services</b> concentram as regras; <b>models</b> descrevem as tabelas; <b>schemas</b> definem a validação de entrada. As chamadas a serviços externos ficam isoladas em <code>integracoes.py</code>, o que permite simulá-las nos testes.</p>
<h2>Fluxo de uma requisição (agenda do dia)</h2>
<ol>
<li>A view <code>AgendaView.vue</code> chama <code>GET /api/legislation/agenda?data=...</code>.</li>
<li>A rota valida os parâmetros com <code>AgendaQuery</code>; dado inválido gera resposta 422 com a mensagem de cada campo.</li>
<li><code>obter_ou_criar_agenda</code> procura o dia no banco. Se não existir, consulta eventos e pautas da Câmara e feriados na Brasil API, grava tudo e confirma a transação.</li>
<li><code>montar_agenda</code> aplica o filtro (Plenário, comissões, parlamentares seguidos) e devolve o JSON.</li>
<li>Falhas externas viram erro 502 em português, sem gravar dados parciais.</li>
</ol>
</section>"""


def secao_codigo():
    blocos = [
        '<section class="nova"><h1>5. Detalhamento técnico do código</h1>',
        "<h2>5.1 Application Factory e configuração por ambiente</h2>",
        definicao("politica/__init__.py", "create_app"),
        "<p>A chave secreta padrão só é aceita em modo de desenvolvimento; em produção o aplicativo se recusa a iniciar sem uma chave própria definida no ambiente.</p>",
        "<h2>5.2 Validação no servidor com Pydantic</h2>",
        definicao("politica/auth/schemas.py", "RegistroIn"),
        definicao("politica/validacao.py", "validar"),
        "<p>Os schemas descrevem as regras (tamanhos, formato de e-mail, tipos). A função <code>validar</code> converte os erros do Pydantic em mensagens em português por campo, e o handler de <code>ErroValidacao</code> devolve 422. O frontend exibe cada mensagem junto ao campo correspondente.</p>",
        "<h2>5.3 Autenticação por sessão</h2>",
        definicao("politica/auth/services.py", "registrar_usuario"),
        definicao("politica/auth/decorators.py", "login_required"),
        "<p>A senha é salva com <code>generate_password_hash</code>. A identidade do usuário vem sempre da sessão no servidor; nenhuma rota aceita <code>usuario_id</code> vindo do cliente. A mesma mensagem é devolvida para e-mail ou senha incorretos, para não revelar quais e-mails existem.</p>",
        "<h2>5.4 Rotas e blueprints</h2>",
        definicao("politica/legislation/routes.py", "agenda_do_dia"),
        definicao("politica/legislation/routes.py", "seguir"),
        "<h2>5.5 Cache de agenda e tratamento de falhas externas</h2>",
        definicao("politica/legislation/services.py", "obter_ou_criar_agenda"),
        "<p>O dia é consultado nas APIs externas apenas uma vez. Se a Câmara falhar, a transação é desfeita e nada fica salvo pela metade. Se duas requisições tentarem criar o mesmo dia ao mesmo tempo, a restrição única do banco dispara um <code>IntegrityError</code>, tratado devolvendo a agenda gravada pela outra requisição.</p>",
        "<h2>5.6 Cliente das APIs externas com retry</h2>",
        definicao("politica/legislation/integracoes.py", "_buscar_json"),
        definicao("politica/legislation/integracoes.py", "_sessao"),
        "<h2>5.7 Regras de negócio: destaque dos parlamentares seguidos</h2>",
        definicao("politica/legislation/services.py", "montar_agenda"),
        "<h2>5.8 Modelo com restrições de integridade</h2>",
        definicao("politica/legislation/models.py", "Historico"),
        "<h2>5.9 Testes automatizados</h2>",
        definicao("tests/test_agenda.py", "test_falha_da_camara_retorna_502_e_nao_grava_agenda"),
        definicao("tests/test_agenda.py", "test_projetos_de_parlamentar_seguido_aparecem_destacados"),
        "<p>As integrações externas são substituídas por simulações (<code>monkeypatch</code>), de modo que os testes são rápidos, determinísticos e rodam sem internet.</p>",
        "<h2>5.10 Frontend: carregamento de dados sem condição de corrida</h2>",
        bloco_de_codigo(
            fonte_entre_marcas("frontend/src/views/AgendaView.vue", "let ultimaRequisicao", "watch([data"),
            "javascript",
            "frontend/src/views/AgendaView.vue - carregar()",
        ),
        "<p>Um contador de requisição descarta respostas antigas quando o usuário troca de data rapidamente, evitando que um dia lento sobrescreva o dia atual.</p>",
        "</section>",
    ]
    return "".join(blocos)


def secao_tecnologias():
    return """
<section>
<h1>6. Tecnologias utilizadas e justificativas</h1>
<table>
<tr><th style="width:24%">Tecnologia</th><th>Uso e justificativa</th></tr>
<tr><td>Flask 3</td><td>Framework do backend, conforme as aulas. Application Factory e Blueprints permitem organizar o projeto em módulos testáveis.</td></tr>
<tr><td>SQLAlchemy 2 + Flask-SQLAlchemy</td><td>ORM com modelos tipados (<code>Mapped</code>), relacionamentos e restrições declarados no código.</td></tr>
<tr><td>Alembic (Flask-Migrate)</td><td>Versiona o esquema do banco; qualquer pessoa recria as tabelas com <code>flask db upgrade</code>.</td></tr>
<tr><td>SQLite</td><td>Banco previsto na proposta; não exige instalação e atende ao volume do projeto. A troca para outro SGBD exige apenas mudar <code>DATABASE_URL</code>.</td></tr>
<tr><td>Pydantic 2</td><td>Validação de entrada declarativa no servidor. Substitui Flask-WTF porque o frontend é uma SPA que envia JSON, e não formulários HTML.</td></tr>
<tr><td>Vue 3 + Vite</td><td>Frontend previsto na proposta. Componentes reutilizáveis, rotas no cliente e recarga instantânea no desenvolvimento.</td></tr>
<tr><td>Tailwind CSS</td><td>Framework de CSS utilitário; entrega o layout responsivo (menu lateral no desktop, barra inferior no celular).</td></tr>
<tr><td>Google Gemini</td><td>Gera resumo, impacto e comparação internacional em linguagem simples, respondendo em JSON validado pelo backend.</td></tr>
<tr><td>API da Câmara e Brasil API</td><td>Fontes abertas e gratuitas de pautas, votações, deputados e feriados.</td></tr>
<tr><td>pytest e Vitest</td><td>Testes do backend e do frontend. Ruff faz lint e formatação do Python.</td></tr>
</table>
<h2>Decisões que se afastam da proposta original</h2>
<ul>
<li><b>E-mail e senha no lugar do OAuth do Google.</b> O OAuth exige projeto e credenciais no Google Cloud, o que não cabia no prazo. A autenticação própria usa hash de senha e sessão em cookie <code>HttpOnly</code>, e a identidade nunca vem do cliente.</li>
<li><b>Exportação .ics no lugar da Google Calendar API.</b> Sem o token do Google não há como gravar na agenda do usuário. O arquivo <code>.ics</code> é um padrão aberto aceito pelos principais calendários e cumpre o mesmo objetivo de lembrar a data da votação.</li>
<li><b>Apenas a Câmara dos Deputados.</b> O Senado usa outra API com outro formato; ficou como evolução futura.</li>
</ul>
</section>"""


def secao_criterios(backend, frontend):
    return f"""
<section>
<h1>7. Atendimento aos critérios de avaliação</h1>
<table>
<tr><th style="width:4%">#</th><th style="width:24%">Critério</th><th>Como foi atendido</th></tr>
<tr><td>1</td><td>Arquitetura modular e fábrica de aplicação</td><td><code>create_app(config_class)</code> em <code>politica/__init__.py</code>; configurações Development, Production e Testing; extensões em <code>extensions.py</code>.</td></tr>
<tr><td>2</td><td>Módulos, blueprints e rotas</td><td>Três blueprints (<code>auth</code>, <code>legislation</code>, <code>calendar_sync</code>), cada um com routes, services, models e schemas. Rotas só orquestram; regras ficam nos services.</td></tr>
<tr><td>3</td><td>Formulários e validação</td><td>Validação no servidor com Pydantic (<code>validacao.py</code>) em cadastro, login, agenda, calendário, busca, parlamentares e votações. No Vue, os formulários validam no cliente e exibem os erros do servidor junto de cada campo.</td></tr>
<tr><td>4</td><td>Interface e frontend</td><td>SPA em Vue 3 com Tailwind. Layout responsivo testado de 320 px a desktop: menu lateral fixo e barra de navegação inferior no celular. Estados de carregando, vazio e erro com nova tentativa.</td></tr>
<tr><td>5</td><td>Testes automatizados</td><td>{backend} testes de backend (rotas, serviços, validação, integrações simuladas, cache, concorrência) e {frontend} testes de frontend (utilitários, cliente HTTP, componentes).</td></tr>
<tr><td>6</td><td>Persistência e ORM</td><td>SQLAlchemy 2 com 8 tabelas, relacionamentos 1:N e N:N, restrições de unicidade, chaves estrangeiras com cascade, paginação e consultas agregadas (calendário). Migrations com Alembic.</td></tr>
<tr><td>7</td><td>Qualidade, organização e boas práticas</td><td>Variáveis de ambiente com <code>.env</code> e <code>.env.example</code>; logging configurado; handlers de erro padronizados em JSON; timeout e retry nas integrações; lint e formatação com Ruff; histórico de commits por funcionalidade na branch <code>dev</code>; README com instruções.</td></tr>
</table>
<h2>Números do projeto</h2>
<table>
<tr><td style="width:50%">Linhas de código Python (aplicação)</td><td>{total_de_linhas(["politica/**/*.py"])}</td></tr>
<tr><td>Linhas de testes Python</td><td>{total_de_linhas(["tests/*.py"])}</td></tr>
<tr><td>Linhas de frontend (Vue e JavaScript)</td><td>{total_de_linhas(["frontend/src/**/*.vue", "frontend/src/**/*.js"])}</td></tr>
<tr><td>Testes automatizados (backend / frontend)</td><td>{backend} / {frontend}</td></tr>
</table>
</section>"""


def secao_execucao():
    return """
<section>
<h1>8. Como executar o projeto</h1>
<h2>Pré-requisitos</h2>
<ul><li>Python 3.10 ou superior</li><li>Node.js 20 ou superior</li></ul>
<h2>Backend</h2>
<pre class="bloco" style="border-top:1px solid #e2e8f0;border-radius:4px">python3 -m venv venv
source venv/bin/activate          # no Windows: venv\\Scripts\\activate
pip install -e ".[dev]"
cp .env.example .env              # opcional: preencher GEMINI_API_KEY
flask db upgrade                  # cria as tabelas
flask importar-parlamentares      # importa os 513 deputados
flask run                         # API em http://localhost:5001</pre>
<h2>Frontend</h2>
<pre class="bloco" style="border-top:1px solid #e2e8f0;border-radius:4px">cd frontend
npm install
npm run dev                       # http://localhost:5173</pre>
<h2>Uso</h2>
<ol>
<li>Abra <code>http://localhost:5173</code> e navegue pela Agenda, Votações, Calendário, Busca e Parlamentares.</li>
<li>Crie uma conta em <b>Entrar → Cadastre-se</b> para seguir parlamentares, gerar resumos com IA e exportar para o calendário.</li>
<li>Os resumos de IA exigem <code>GEMINI_API_KEY</code> no arquivo <code>.env</code>. Sem a chave a API responde 503 com uma mensagem clara e o restante do sistema funciona normalmente.</li>
</ol>
<h2>Testes e qualidade</h2>
<pre class="bloco" style="border-top:1px solid #e2e8f0;border-radius:4px">pytest                              # testes do backend
ruff check . &amp;&amp; ruff format --check .  # lint e formatação
cd frontend &amp;&amp; npm test                 # testes do frontend</pre>
<div class="aviso">No macOS a porta 5000 é ocupada pelo AirPlay Receiver. Por isso o backend usa a porta 5001, definida em <code>.flaskenv</code>.</div>
</section>"""


def secao_desafios():
    return """
<section>
<h1>9. Principais desafios e soluções</h1>
<table>
<tr><th style="width:30%">Desafio</th><th>Solução</th></tr>
<tr><td>O formato real da API da Câmara era diferente do que o código inicial assumia (a pauta traz a proposição aninhada e a votação usa <code>aprovacao</code> numérico, não booleano).</td><td>Antes de implementar, consultamos os endpoints reais e ajustamos o código e os dados de teste aos formatos observados.</td></tr>
<tr><td>Volume de dados: um dia de comissões chegava a 499 itens e a primeira carga demorava 24 s.</td><td>Filtramos os tipos que o cidadão reconhece (PL, PLP, PEC, PDL, MPV etc.) e vinculamos autores só aos projetos do Plenário. O feed passou a mostrar o Plenário por padrão e a carga inicial caiu para cerca de 5 s; depois disso o dia vem do cache.</td></tr>
<tr><td>Ruído nas votações: de 112 registros semanais, 102 eram requerimentos e mudanças de regime de tramitação.</td><td>Descartamos votações procedimentais e aceitamos votações de mérito mesmo sem objeto, reconhecendo-as pela descrição. Restaram 10 votações relevantes.</td></tr>
<tr><td>Instabilidade da API externa: um evento lento derrubava a agenda inteira.</td><td>Timeout, retry com backoff exponencial, erro 502 com mensagem clara, transação desfeita (sem agenda parcial) e, nas votações, uso dos dados já salvos quando a Câmara está fora do ar.</td></tr>
<tr><td>Segurança: o código inicial aceitava <code>usuario_id</code> e dados de login vindos do cliente sem validar.</td><td>Autenticação por e-mail e senha com hash, identidade apenas pela sessão do servidor e decorator <code>login_required</code>.</td></tr>
<tr><td>Condição de corrida: duas requisições para um dia novo geravam erro 500 por violar a unicidade.</td><td>Tratamento do <code>IntegrityError</code> reaproveitando a agenda gravada pela outra requisição, com teste que reproduz a corrida.</td></tr>
<tr><td>Respostas inesperadas da IA (JSON incompleto) poderiam gravar campos vazios.</td><td>Validação do JSON retornado; fora do formato, o usuário recebe erro 502 e nada é salvo.</td></tr>
<tr><td>Curingas do SQL na busca: digitar <code>%%</code> casava com todos os registros.</td><td>Uso de <code>icontains(autoescape=True)</code> e comparação exata no filtro de partido, com testes.</td></tr>
<tr><td>Porta 5000 ocupada pelo AirPlay no macOS: as chamadas retornavam 403.</td><td>Backend movido para a porta 5001 e documentado no README.</td></tr>
<tr><td>Barra de navegação do celular cortava itens em telas de 360 px.</td><td>Detectado em teste visual; os itens passaram a dividir a largura igualmente e o rótulo longo ganhou versão curta. Verificado de 320 px em diante.</td></tr>
</table>
</section>"""


def secao_limitacoes():
    return """
<section>
<h1>10. Limitações e próximos passos</h1>
<ul>
<li>Apenas a Câmara dos Deputados é consultada; Senado e sessões do Congresso Nacional ficam para uma próxima versão.</li>
<li>A autoria de projetos só é vinculada aos parlamentares para pautas do Plenário; nas comissões o destaque por “seguir” não se aplica.</li>
<li>A busca global procura apenas nos dados já consultados e salvos no banco.</li>
<li>Os resumos de IA dependem de uma chave do Gemini configurada; os testes cobrem o fluxo com respostas simuladas.</li>
<li>Próximos passos: OAuth do Google com Google Calendar API, dados do Senado, votos individuais por parlamentar e notificações.</li>
</ul>
</section>"""


def montar_html():
    app = create_app(TestingConfig)
    with app.app_context():
        metadados = db.metadata
        backend, frontend = total_de_testes()
        corpo = [
            capa(),
            sumario(),
            secao_descricao(),
            secao_telas(),
            secao_er(metadados),
            secao_arquitetura(),
            secao_codigo(),
            secao_tecnologias(),
            secao_criterios(backend, frontend),
            secao_execucao(),
            secao_desafios(),
            secao_limitacoes(),
        ]
    estilo_codigo = HtmlFormatter(style="friendly").get_style_defs("pre")
    return (
        '<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"/>'
        "<title>Política Simplificada - Documentação</title>"
        f"<style>{CSS}{estilo_codigo}</style></head><body>" + "".join(corpo) + "</body></html>"
    )


if __name__ == "__main__":
    destino = DOCS / "documentacao.html"
    destino.write_text(montar_html())
    print(destino)
