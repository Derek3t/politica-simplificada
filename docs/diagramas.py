from html import escape

LARGURA_CAIXA = 250
ALTURA_LINHA = 18
ALTURA_CABECALHO = 26

POSICOES = {
    "usuarios": (10, 10),
    "usuario_parlamentar": (375, 10),
    "parlamentar": (740, 10),
    "agenda": (10, 235),
    "projetos_lei": (375, 235),
    "historico": (740, 235),
    "dias_especiais": (10, 385),
    "votacoes": (740, 400),
}

SELO_COR = {"PK": "#b45309", "FK": "#1d4ed8", "UK": "#047857"}


def _colunas_unicas(tabela):
    unicas = {c.name for c in tabela.columns if c.unique}
    for indice in tabela.indexes:
        if indice.unique and len(indice.columns) == 1:
            unicas.update(c.name for c in indice.columns)
    return unicas


def _restricoes_compostas(tabela):
    return [
        ", ".join(c.name for c in restricao.columns)
        for restricao in tabela.constraints
        if restricao.__class__.__name__ == "UniqueConstraint" and len(restricao.columns) > 1
    ]


def _selos(coluna, unicas):
    selos = []
    if coluna.primary_key:
        selos.append("PK")
    if coluna.foreign_keys:
        selos.append("FK")
    if coluna.name in unicas:
        selos.append("UK")
    return selos


def _altura(tabela):
    extras = len(_restricoes_compostas(tabela))
    return ALTURA_CABECALHO + (len(tabela.columns) + extras) * ALTURA_LINHA + 8


def _caixa(tabela, x, y):
    unicas = _colunas_unicas(tabela)
    partes = [
        f'<rect x="{x}" y="{y}" width="{LARGURA_CAIXA}" height="{_altura(tabela)}" rx="6" fill="#fff" stroke="#0c1b3d" stroke-width="1.4"/>',
        f'<path d="M{x} {y + 26} V{y + 6} a6 6 0 0 1 6 -6 H{x + LARGURA_CAIXA - 6} a6 6 0 0 1 6 6 V{y + 26} Z" fill="#0c1b3d"/>',
        f'<text x="{x + 10}" y="{y + 17}" fill="#fff" font-size="12.5" font-weight="700">{escape(tabela.name)}</text>',
    ]
    for posicao, coluna in enumerate(tabela.columns):
        base = y + ALTURA_CABECALHO + posicao * ALTURA_LINHA + 13
        selos = _selos(coluna, unicas)
        for ordem, selo in enumerate(selos):
            partes.append(
                f'<text x="{x + 8 + ordem * 22}" y="{base}" font-size="8.5" font-weight="700" fill="{SELO_COR[selo]}">{selo}</text>'
            )
        peso = "700" if coluna.primary_key else "400"
        partes.append(f'<text x="{x + 54}" y="{base}" font-size="11" font-weight="{peso}">{escape(coluna.name)}</text>')
        partes.append(
            f'<text x="{x + LARGURA_CAIXA - 8}" y="{base}" font-size="9.5" fill="#64748b" text-anchor="end">'
            f"{escape(str(coluna.type))}</text>"
        )
    for ordem, composta in enumerate(_restricoes_compostas(tabela)):
        base = y + ALTURA_CABECALHO + (len(tabela.columns) + ordem) * ALTURA_LINHA + 13
        partes.append(f'<text x="{x + 8}" y="{base}" font-size="9.5" fill="#047857">UK ({escape(composta)})</text>')
    return "\n".join(partes)


def _ponto(tabela, lado):
    x, y = POSICOES[tabela.name]
    altura = _altura(tabela)
    if lado == "esquerda":
        return x, y + altura / 2
    if lado == "direita":
        return x + LARGURA_CAIXA, y + altura / 2
    if lado == "topo":
        return x + LARGURA_CAIXA / 2, y
    return x + LARGURA_CAIXA / 2, y + altura


def _lados(filha, mae):
    fx, fy = POSICOES[filha.name]
    mx, my = POSICOES[mae.name]
    if abs(fx - mx) > abs(fy - my):
        return ("esquerda", "direita") if fx > mx else ("direita", "esquerda")
    return ("topo", "base") if fy > my else ("base", "topo")


def _relacionamento(filha, mae):
    lado_filha, lado_mae = _lados(filha, mae)
    x1, y1 = _ponto(filha, lado_filha)
    x2, y2 = _ponto(mae, lado_mae)
    desloca = {"esquerda": (-10, -5), "direita": (10, -5), "topo": (8, -6), "base": (8, 14)}
    dx1, dy1 = desloca[lado_filha]
    dx2, dy2 = desloca[lado_mae]
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#475569" stroke-width="1.4"/>'
        f'<text x="{x1 + dx1}" y="{y1 + dy1}" font-size="11" font-weight="700" fill="#0c1b3d" text-anchor="middle">N</text>'
        f'<text x="{x2 + dx2}" y="{y2 + dy2}" font-size="11" font-weight="700" fill="#0c1b3d" text-anchor="middle">1</text>'
    )


def diagrama_er(metadados):
    tabelas = metadados.tables
    linhas = []
    for tabela in tabelas.values():
        for coluna in tabela.columns:
            for chave in coluna.foreign_keys:
                linhas.append(_relacionamento(tabela, chave.column.table))
    caixas = [_caixa(tabelas[nome], x, y) for nome, (x, y) in POSICOES.items()]
    return (
        '<svg viewBox="0 0 1000 590" xmlns="http://www.w3.org/2000/svg" font-family="Helvetica, Arial, sans-serif">'
        + "".join(linhas)
        + "".join(caixas)
        + "</svg>"
    )


def _caixa_generica(x, y, largura, altura, titulo, linhas, cor_fundo="#fff", cor_titulo="#0c1b3d"):
    partes = [
        f'<rect x="{x}" y="{y}" width="{largura}" height="{altura}" rx="8" fill="{cor_fundo}" stroke="{cor_titulo}" stroke-width="1.4"/>',
        f'<text x="{x + largura / 2}" y="{y + 20}" font-size="12.5" font-weight="700" fill="{cor_titulo}" text-anchor="middle">{escape(titulo)}</text>',
    ]
    for ordem, linha in enumerate(linhas):
        partes.append(
            f'<text x="{x + largura / 2}" y="{y + 40 + ordem * 16}" font-size="10.5" fill="#334155" text-anchor="middle">{escape(linha)}</text>'
        )
    return "".join(partes)


def _seta(x1, y1, x2, y2, rotulo="", deslocamento=(0, -6)):
    texto = ""
    if rotulo:
        texto = (
            f'<text x="{(x1 + x2) / 2 + deslocamento[0]}" y="{(y1 + y2) / 2 + deslocamento[1]}" '
            f'font-size="10" fill="#475569" text-anchor="middle">{escape(rotulo)}</text>'
        )
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#475569" stroke-width="1.5" marker-end="url(#ponta)"/>'
        + texto
    )


def diagrama_arquitetura():
    definicao = (
        '<defs><marker id="ponta" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">'
        '<path d="M0 0 L8 4 L0 8 Z" fill="#475569"/></marker></defs>'
    )
    caixas = [
        _caixa_generica(
            10,
            40,
            300,
            150,
            "Frontend (Vue 3 + Vite + Tailwind)",
            [
                "views: Agenda, Votações, Calendário,",
                "Busca, Parlamentares, Login",
                "components: modais, cards, paginação",
                "api/: cliente HTTP (fetch)",
                "composables/useAuth",
            ],
            "#eef4ff",
            "#1d4ed8",
        ),
        _caixa_generica(350, 10, 440, 410, "Backend (Flask) - create_app()", [], "#f8fafc", "#0c1b3d"),
        _caixa_generica(
            365,
            50,
            200,
            120,
            "Blueprints (routes)",
            ["auth, legislation, calendar_sync", "recebem a requisição", "validam a entrada (Pydantic)"],
        ),
        _caixa_generica(
            585,
            50,
            190,
            120,
            "Services",
            ["regras de negócio", "cache de agenda e votações", "filtros, busca e calendário"],
        ),
        _caixa_generica(
            585,
            215,
            190,
            100,
            "Models (SQLAlchemy)",
            ["8 tabelas", "constraints de unicidade", "migrations com Alembic"],
        ),
        _caixa_generica(585, 355, 190, 55, "SQLite", ["politica.db"], "#ecfdf5", "#047857"),
        _caixa_generica(
            365,
            215,
            200,
            100,
            "Infra transversal",
            ["extensions.py e config.py (.env)", "errors.py (handlers JSON)", "logging"],
        ),
        _caixa_generica(
            820,
            50,
            170,
            120,
            "Integrações",
            ["integracoes.py", "timeout + tentativas", "isoladas para os testes"],
            "#fff7ed",
            "#c2410c",
        ),
        _caixa_generica(
            820,
            215,
            170,
            100,
            "Serviços externos",
            ["API da Câmara", "Brasil API (feriados)", "Google Gemini (IA)"],
            "#fff7ed",
            "#c2410c",
        ),
    ]
    setas = [
        _seta(310, 115, 365, 110),
        _seta(565, 110, 585, 110),
        _seta(680, 170, 680, 215),
        _seta(680, 315, 680, 355),
        _seta(775, 110, 820, 110),
        _seta(905, 170, 905, 215),
    ]
    rotulos = (
        '<text x="338" y="100" font-size="9" fill="#475569" text-anchor="middle">/api</text>'
        '<text x="912" y="198" font-size="9" fill="#475569">HTTPS</text>'
    )
    return (
        '<svg viewBox="0 0 1000 430" xmlns="http://www.w3.org/2000/svg" font-family="Helvetica, Arial, sans-serif">'
        + definicao
        + "".join(caixas)
        + "".join(setas)
        + rotulos
        + "</svg>"
    )
