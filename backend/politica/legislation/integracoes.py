import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor

import requests
from flask import current_app
from openrouter import OpenRouter
from openrouter.errors import OpenRouterError

from politica.errors import ErroApi, ErroServicoExterno

logger = logging.getLogger(__name__)

ID_ORGAO_PLENARIO = 180
TENTATIVAS = 3
PAUSA_ENTRE_TENTATIVAS = 0.5
MAX_PAGINAS_VOTACOES = 6
HEADERS_JSON = {"Accept": "application/json"}
TIMEOUT_IA_MS = 30_000
MAX_TOKENS_IA = 2000

CAMPOS_ANALISE = ("resumo", "analise_impacto", "comparacao_internacional")
CAMPOS_DIA_ESPECIAL = ("contexto_historico", "importancia", "impacto_legislativo")

PROMPT_ANALISE = """Você é um cientista político e educador cívico que traduz o Congresso Brasileiro
para cidadãos comuns.
Analise a proposição abaixo e responda apenas com um JSON contendo as chaves:
"resumo": o que significa, em linguagem simples e no máximo 3 frases;
"analise_impacto": como isso muda o dia a dia do cidadão;
"comparacao_internacional": se países desenvolvidos têm algo parecido ou qual a tendência global.

Proposição: {texto}"""

PROMPT_DIA_ESPECIAL = """Você é um educador cívico que explica datas importantes do Brasil para cidadãos comuns.
Explique a data "{nome}" ({data}) e responda apenas com um JSON contendo as chaves:
"contexto_historico": origem e significado histórico da data, em até 4 frases;
"importancia": por que a data é importante hoje, em até 3 frases;
"impacto_legislativo": como o tema se relaciona com leis e projetos em tramitação no Congresso, em até 3 frases.
Não invente fatos; se não souber, diga que a informação não está disponível."""


def _buscar_json(url, params, timeout, servico, headers=None):
    for tentativa in range(1, TENTATIVAS + 1):
        try:
            resposta = requests.get(url, params=params, timeout=timeout, headers=headers)
            resposta.raise_for_status()
            return resposta.json()
        except (requests.RequestException, ValueError) as erro:
            logger.warning(
                "Falha ao consultar %s em %s (tentativa %s de %s): %s", servico, url, tentativa, TENTATIVAS, erro
            )
            if tentativa == TENTATIVAS:
                raise ErroServicoExterno(f"{servico} indisponível no momento.") from erro
            time.sleep(PAUSA_ENTRE_TENTATIVAS * tentativa)


def _camara(caminho, **params):
    url = current_app.config["CAMARA_BASE_URL"] + caminho
    resposta = _buscar_json(url, params, current_app.config["HTTP_TIMEOUT"], "API da Câmara")
    return resposta.get("dados", [])


def listar_deputados():
    deputados, pagina = [], 1
    while True:
        lote = _camara("/deputados", itens=100, pagina=pagina, ordem="ASC", ordenarPor="nome")
        deputados.extend(lote)
        if len(lote) < 100:
            return deputados
        pagina += 1


def eventos_do_dia(data):
    return _camara(
        "/eventos",
        dataInicio=data.isoformat(),
        dataFim=data.isoformat(),
        itens=100,
        ordem="ASC",
        ordenarPor="dataHoraInicio",
    )


def votacoes_do_periodo(inicio, fim):
    votacoes = []
    for pagina in range(1, MAX_PAGINAS_VOTACOES + 1):
        lote = _camara(
            "/votacoes",
            dataInicio=inicio.isoformat(),
            dataFim=fim.isoformat(),
            idOrgao=ID_ORGAO_PLENARIO,
            itens=100,
            pagina=pagina,
            ordem="DESC",
            ordenarPor="dataHoraRegistro",
        )
        votacoes.extend(lote)
        if len(lote) < 100:
            break
    return votacoes


def pautas_dos_eventos(ids_eventos):
    base = current_app.config["CAMARA_BASE_URL"]
    timeout = current_app.config["HTTP_TIMEOUT"]

    def buscar(id_evento):
        resposta = _buscar_json(f"{base}/eventos/{id_evento}/pauta", None, timeout, "API da Câmara")
        return resposta.get("dados", [])

    with ThreadPoolExecutor(max_workers=8) as pool:
        return list(pool.map(buscar, ids_eventos))


def autores_das_proposicoes(ids_proposicoes):
    base = current_app.config["CAMARA_BASE_URL"]
    timeout = current_app.config["HTTP_TIMEOUT"]

    def buscar(id_proposicao):
        try:
            resposta = _buscar_json(f"{base}/proposicoes/{id_proposicao}/autores", None, timeout, "API da Câmara")
        except ErroServicoExterno:
            return []
        autores = resposta.get("dados", [])
        return [int(a["uri"].rsplit("/", 1)[-1]) for a in autores if "/deputados/" in a.get("uri", "")]

    with ThreadPoolExecutor(max_workers=8) as pool:
        return dict(zip(ids_proposicoes, pool.map(buscar, ids_proposicoes), strict=True))


def votos_de_votacoes(ids_votacoes):
    base = current_app.config["CAMARA_BASE_URL"]
    timeout = current_app.config["HTTP_TIMEOUT"]

    def buscar(id_votacao):
        try:
            resposta = _buscar_json(f"{base}/votacoes/{id_votacao}/votos", None, timeout, "API da Câmara")
        except ErroServicoExterno:
            return None
        return [
            {"id_deputado": voto["deputado_"]["id"], "voto": voto.get("tipoVoto") or "Sem registro"}
            for voto in resposta.get("dados", [])
        ]

    with ThreadPoolExecutor(max_workers=8) as pool:
        return dict(zip(ids_votacoes, pool.map(buscar, ids_votacoes), strict=True))


def _senado(caminho, **params):
    url = current_app.config["SENADO_BASE_URL"] + caminho
    return _buscar_json(url, params, current_app.config["HTTP_TIMEOUT"], "API do Senado", HEADERS_JSON)


def listar_senadores():
    resposta = _senado("/senador/lista/atual")
    try:
        senadores = resposta["ListaParlamentarEmExercicio"]["Parlamentares"]["Parlamentar"]
    except (KeyError, TypeError) as erro:
        raise ErroServicoExterno("API do Senado devolveu um formato inesperado.") from erro
    return [
        {
            "id": int(s["IdentificacaoParlamentar"]["CodigoParlamentar"]),
            "nome": s["IdentificacaoParlamentar"]["NomeParlamentar"],
            "siglaPartido": s["IdentificacaoParlamentar"]["SiglaPartidoParlamentar"],
            "siglaUf": s["IdentificacaoParlamentar"]["UfParlamentar"],
            "urlFoto": s["IdentificacaoParlamentar"].get("UrlFotoParlamentar"),
        }
        for s in senadores
    ]


def votacoes_senado(inicio, fim):
    return _senado("/votacao", dataInicio=inicio.isoformat(), dataFim=fim.isoformat())


def feriados_do_ano(ano):
    url = f"{current_app.config['BRASIL_API_URL']}/{ano}"
    return _buscar_json(url, None, current_app.config["HTTP_TIMEOUT"], "Brasil API")


def _gerar_json(prompt, campos):
    chave = current_app.config["OPENROUTER_API_KEY"]
    if not chave:
        raise ErroApi("Chave da IA não configurada.", 503)

    try:
        with OpenRouter(api_key=chave, timeout_ms=TIMEOUT_IA_MS) as cliente:
            resposta = cliente.chat.send(
                model=current_app.config["OPENROUTER_MODEL"],
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=MAX_TOKENS_IA,
            )
        texto = resposta.choices[0].message.content
        dados = json.loads(texto)
    except (OpenRouterError, IndexError, ValueError, TypeError) as erro:
        logger.exception("Falha ao gerar conteúdo com a IA")
        raise ErroServicoExterno("Não foi possível gerar a análise com IA.") from erro

    if not isinstance(dados, dict) or not all(isinstance(dados.get(campo), str) and dados[campo] for campo in campos):
        logger.error("Resposta da IA fora do formato esperado: %s", texto)
        raise ErroServicoExterno("A IA devolveu uma resposta incompleta. Tente novamente.")

    return {campo: dados[campo] for campo in campos}


def analisar_com_ia(texto):
    return _gerar_json(PROMPT_ANALISE.format(texto=texto), CAMPOS_ANALISE)


def contextualizar_dia_especial(nome, data):
    return _gerar_json(PROMPT_DIA_ESPECIAL.format(nome=nome, data=data), CAMPOS_DIA_ESPECIAL)
