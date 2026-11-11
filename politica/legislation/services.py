from datetime import datetime, date
import requests
from politica.ext.db import db
from politica.auth.models import Usuario
from politica.legislation.models import Parlamentar, UsuarioParlamentar, Agenda, ProjetoLei, DiaEspecial
from google import genai
from flask import current_app

BASE_URL_CAMARA = "https://dadosabertos.camara.leg.br/api/v2"
BASE_URL_BRASIL_API = "https://brasilapi.com.br/api/feriados/v1"

def gerar_resumo_projeto_lei(titulo_ou_texto: str) -> str:
    """
    Gera a tradução do 'juridiquês' usando o Gemini com os 3 pontos da proposta de valor.
    Retorna uma string em Markdown.
    """
    api_key = current_app.config.get("GEMINI_API_KEY")
    if not api_key:
        return "Resumo indisponível (Chave de IA não configurada)."
        
    try:
        client = genai.Client(api_key=api_key)
        prompt = f"""
        Atue como um cientista político e educador cívico especializado em traduzir o Congresso Brasileiro para cidadãos comuns.
        Analise o seguinte projeto de lei/pauta:
        "{titulo_ou_texto}"

        Retorne a resposta estruturada exatamente nos seguintes tópicos em Markdown:
        1. **O que significa?** (Explicação em uma linguagem extremamente simples, sem juridiquês, em até 3 frases).
        2. **Impacto Prático** (Como isso muda o dia a dia do cidadão brasileiro).
        3. **Panorama Internacional** (Breve menção se países desenvolvidos possuem algo similar ou qual a tendência global sobre o tema).
        """
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"Erro ao gerar resumo com IA: {str(e)}"

def seguir_parlamentar(usuario_id: int, parlamentar_id: int) -> dict:
    usuario = Usuario.query.get(usuario_id)
    parlamentar = Parlamentar.query.get(parlamentar_id)
    
    if not usuario or not parlamentar:
        return {"sucesso": False, "erro": "Usuário ou parlamentar não encontrado."}, 404
        
    # Verifica se já segue para evitar duplicidade
    ja_segue = UsuarioParlamentar.query.filter_by(
        usuario_id=usuario_id, 
        parlamentar_id=parlamentar_id
    ).first()
    
    if ja_segue:
        return {"sucesso": False, "erro": "Você já segue este parlamentar."}, 400
        
    novo_seguimento = UsuarioParlamentar(usuario_id=usuario_id, parlamentar_id=parlamentar_id)
    db.session.add(novo_seguimento)
    db.session.commit()
    
    return {"sucesso": True, "mensagem": f"Agora você está seguindo {parlamentar.nome}."}

def filtrar_projetos_por_usuario(agenda: Agenda, usuario_id: int | None):
    """
    Filtra ou destaca os projetos da agenda com base em quem o usuário segue.
    """
    parlamentares_seguidos_ids = set()
    if usuario_id:
        usuario = Usuario.query.get(usuario_id)
        if usuario:
            parlamentares_seguidos_ids = {p.parlamentar_id for p in usuario.parlamentares_seguidos}

    projetos_serializados = []
    for p in agenda.projetos_lei:
        h_ids = {h.parlamentar_id for h in p.historicos}
        envolve_seguido = bool(h_ids.intersection(parlamentares_seguidos_ids)) if parlamentares_seguidos_ids else False
        
        # Se o usuário segue alguém, filtramos para mostrar apenas os projetos dos parlamentares dele.
        # Se não segue ninguém, exibe todos os projetos da agenda global.
        if parlamentares_seguidos_ids and not envolve_seguido:
            continue
            
        projetos_serializados.append({
            "id": p.id,
            "codigo_pl": p.codigo_pl,
            "titulo": p.titulo,
            "resumo": p.resumo,
            "status": p.status,
            "destacado_para_usuario": envolve_seguido
        })

    return projetos_serializados

def obter_ou_criar_agenda_por_data(data_str: str) -> Agenda:
    """
    Verifica se a data existe no banco local. 
    Se não existir, consome a Câmara API e Brasil API, processa via IA e salva.
    """
    data_alvo = datetime.strptime(data_str, "%Y-%m-%d").date()
    
    # 1. Tenta buscar do banco local (Cache Global)
    agenda = Agenda.query.filter_by(date=data_alvo).first()
    if agenda:
        return agenda
        
    # 2. Se não existe, cria a estrutura da agenda para o dia
    agenda = Agenda(date=data_alvo, resumo=f"Resumo diário consolidado para {data_str}")
    db.session.add(agenda)
    db.session.flush() # Gera o ID da agenda para associar os filhos
    
    # 3. Busca Feriados (Brasil API)
    ano = data_alvo.year
    try:
        resp_feriados = requests.get(f"{BASE_URL_BRASIL_API}/{ano}")
        if resp_feriados.status_code == 200:
            feriados = resp_feriados.json()
            for f in feriados:
                if f.get("date") == data_str:
                    dia_especial = DiaEspecial(
                        nome=f.get("name"),
                        tipo=f.get("type", "Feriado Nacional"),
                        agenda_ref=agenda.id
                    )
                    db.session.add(dia_especial)
    except Exception:
        pass # Falhas em APIs externas não devem quebrar o fluxo principal

    # 4. Busca Eventos/Pautas da Câmara para o dia
    params = {
        "dataInicio": data_str,
        "dataFim": data_str,
        "ordem": "ASC",
        "ordenarPor": "dataHoraInicio"
    }
    
    try:
        resp_eventos = requests.get(f"{BASE_URL_CAMARA}/eventos", params=params)
        if resp_eventos.status_code == 200:
            eventos = resp_eventos.json().get("dados", [])
            for evento in eventos:
                if evento.get("situacao", "").lower() == "cancelada":
                    continue
                
                evento_id = evento["id"]
                resp_pauta = requests.get(f"{BASE_URL_CAMARA}/eventos/{evento_id}/pauta")
                
                if resp_pauta.status_code == 200:
                    itens_pauta = resp_pauta.json().get("dados", [])
                    for item in itens_pauta:
                        uri_prop = item.get("uriProposicao")
                        ementa_formal = item.get("titulo") or item.get("descricao")
                        
                        if uri_prop:
                            resp_prop = requests.get(uri_prop)
                            if resp_prop.status_code == 200:
                                ementa_formal = resp_prop.json().get("dados", {}).get("ementa", ementa_formal)
                        
                        # Processa a tradução do juridiquês via Gemini
                        resumo_ia = gerar_resumo_projeto_lei(ementa_formal)
                        
                        projeto = ProjetoLei(
                            codigo_pl=item.get("codTipo", "PL") + " " + str(item.get("numero", "")),
                            titulo=ementa_formal[:255],
                            resumo=resumo_ia,
                            status="Em tramitação",
                            data_votacao=data_alvo,
                            agenda_ref=agenda.id
                        )
                        db.session.add(projeto)
    except Exception:
        pass

    db.session.commit()
    return agenda