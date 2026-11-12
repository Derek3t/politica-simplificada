import json
import logging
from concurrent.futures import ThreadPoolExecutor

import requests
from flask import current_app
from google import genai
from google.genai import errors as genai_errors
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from politica.errors import ErroApi, ErroServicoExterno

logger = logging.getLogger(__name__)

ID_ORGAO_PLENARIO = 180
MAX_PAGINAS_VOTACOES = 6

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


def _sessao():
    tentativas = Retry(total=2, backoff_factor=0.5, status_forcelist=(429, 500, 502, 503, 504))
    sessao = requests.Session()
    sessao.mount("https://", HTTPAdapter(max_retries=tentativas))
    return sessao


def _buscar_json(url, params, timeout, servico):
    try:
        resposta = _sessao().get(url, params=params, timeout=timeout)
        resposta.raise_for_status()
        return resposta.json()
    except (requests.RequestException, ValueError) as erro:
        logger.warning("Falha ao consultar %s em %s: %s", servico, url, erro)
        raise ErroServicoExterno(f"{servico} indisponível no momento.") from erro


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


def feriados_do_ano(ano):
    url = f"{current_app.config['BRASIL_API_URL']}/{ano}"
    return _buscar_json(url, None, current_app.config["HTTP_TIMEOUT"], "Brasil API")


def _gerar_json(prompt, campos):
    chave = current_app.config["GEMINI_API_KEY"]
    if not chave:
        raise ErroApi("Chave da IA não configurada.", 503)

    try:
        cliente = genai.Client(api_key=chave)
        resposta = cliente.models.generate_content(
            model=current_app.config["GEMINI_MODEL"],
            contents=prompt,
            config={"response_mime_type": "application/json"},
        )
        dados = json.loads(resposta.text)
    except (genai_errors.APIError, ValueError, TypeError) as erro:
        logger.exception("Falha ao gerar conteúdo com o Gemini")
        raise ErroServicoExterno("Não foi possível gerar a análise com IA.") from erro

    if not isinstance(dados, dict) or not all(isinstance(dados.get(campo), str) and dados[campo] for campo in campos):
        logger.error("Resposta do Gemini fora do formato esperado: %s", resposta.text)
        raise ErroServicoExterno("A IA devolveu uma resposta incompleta. Tente novamente.")

    return {campo: dados[campo] for campo in campos}


def analisar_com_gemini(texto):
    return _gerar_json(PROMPT_ANALISE.format(texto=texto), CAMPOS_ANALISE)


def contextualizar_dia_especial(nome, data):
    return _gerar_json(PROMPT_DIA_ESPECIAL.format(nome=nome, data=data), CAMPOS_DIA_ESPECIAL)
