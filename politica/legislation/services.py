from politica.ext.db import db
from politica.auth.models import Usuario
from politica.legislation.models import Parlamentar, UsuarioParlamentar
from google import genai
from flask import current_app

def gerar_resumo_projeto_lei(titulo_ou_texto: str) -> dict:
    api_key = current_app.config.get("GEMINI_API_KEY")
    if not api_key:
        return {"sucesso": False, "erro": "Chave da API do Gemini não configurada."}
        
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
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return {"sucesso": True, "analise_ia": response.text}
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}


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