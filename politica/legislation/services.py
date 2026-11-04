from google import genai
from flask import current_app

def gerar_resumo_projeto_lei(texto_formal: str) -> dict:
    api_key = current_app.config.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    Atue como um cientista político e educador cívico...
    Texto oficial:
    {texto_formal}
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return {"sucesso": True, "analise_ia": response.text}
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}