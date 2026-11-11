import requests
from datetime import date

BASE_URL = "https://dadosabertos.camara.leg.br/api/v2"

def consultar_eventos_futuros(data_inicio: str, data_fim: str):
    """
    1. Para votações futuras: consulta eventos deliberativos, filtra cancelados,
       busca a pauta e as ementas das proposições.
    """
    url = f"{BASE_URL}/eventos"
    params = {
        "dataInicio": data_inicio,
        "dataFim": data_fim,
        "ordem": "ASC",
        "ordenarPor": "dataHoraInicio"
    }
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return []
        
    eventos = response.json().get("dados", [])
    pautas_processadas = []

    for evento in eventos:
        # Descarta eventos cancelados ou que não sejam deliberativos (ex: audiências públicas simples)
        if evento.get("situacao", "").lower() == "cancelada":
            continue
            
        evento_id = evento["id"]
        # Consulta a pauta do evento específico
        pauta_url = f"{BASE_URL}/eventos/{evento_id}/pauta"
        pauta_resp = requests.get(pauta_url)
        
        if pauta_resp.status_code == 200:
            itens_pauta = pauta_resp.json().get("dados", [])
            for item in itens_pauta:
                uri_proposicao = item.get("uriProposicao")
                if uri_proposicao:
                    # Busca detalhes/ementa da proposição
                    prop_resp = requests.get(uri_proposicao)
                    ementa = prop_resp.json().get("dados", {}).get("ementa") if prop_resp.status_code == 200 else ""
                    
                    pautas_processadas.append({
                        "evento_id": evento_id,
                        "data_prevista": evento.get("dataHoraInicio"),
                        "orgao": evento.get("orgaos", [{}])[0].get("nome"),
                        "materia": item.get("titulo") or item.get("descricao"),
                        "ementa": ementa
                    })
                    
    return pautas_processadas


def consultar_votacoes_realizadas(data_inicio: str, data_fim: str):
    """
    2. Para votações realizadas: consulta as votações do período,
       identifica a matéria e recupera os votos individuais dos parlamentares.
    """
    url = f"{BASE_URL}/votacoes"
    params = {
        "dataInicio": data_inicio,
        "dataFim": data_fim,
        "ordem": "DESC",
        "ordenarPor": "dataHoraRegistro"
    }
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return []
        
    votacoes = response.json().get("dados", [])
    historico_votacoes = []

    for votacao in votacoes:
        votacao_id = votacao["id"]
        
        # Consulta detalhada da votação para pegar o resultado e a proposição associada
        detalhe_url = f"{BASE_URL}/votacoes/{votacao_id}"
        detalhe_resp = requests.get(detalhe_url)
        
        if detalhe_resp.status_code == 200:
            dados_votacao = detalhe_resp.json().get("dados", {})
            
            # Consulta os votos individuais dos parlamentares nesta votação
            votos_url = f"{BASE_URL}/votacoes/{votacao_id}/votos"
            votos_resp = requests.get(votos_url)
            votos_individuais = votos_resp.json().get("dados", []) if votos_resp.status_code == 200 else []
            
            historico_votacoes.append({
                "votacao_id": votacao_id,
                "data": dados_votacao.get("dataHoraRegistro"),
                "resultado": dados_votacao.get("aprovada"), # True/False/None
                "objeto_envolvido": dados_votacao.get("proposicaoObjeto") or dados_votacao.get("descricao"),
                "votos": votos_individuais
            })
            
    return historico_votacoes