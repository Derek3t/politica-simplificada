import google.generativeai as genai
from flask import current_app

def configurar_gemini():
    api_key = current_app.config.get("GEMINI_API_KEY")
    genai.configure(api_key=api_key)

def gerar_resumo_projeto_lei(texto_formal: str) -> dict:
    configurar_gemini()
    
    # Usa o modelo padrão atualizado
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    prompt = f"""
    Atue como um cientista político e educador cívico. Simplifique o seguinte projeto de lei oficial para o cidadão comum, traduzindo o "juridiquês".
    Retorne a resposta estritamente no formato de tópicos claros contendo:
    1. Resumo simples
    2. Análise de impacto prático na sociedade
    3. Contexto ou comparação internacional (se aplicável)

    Texto oficial:
    {texto_formal}
    """
    
    try:
        response = model.generate_content(prompt)
        # Aqui você pode estruturar o parsing do texto gerado conforme sua necessidade
        return {
            "sucesso": True,
            "analise_ia": response.text
        }
    except Exception as e:
        return {
            "sucesso": False,
            "erro": str(e)
        }