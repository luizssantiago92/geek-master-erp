import os
# pyrefly: ignore [missing-import]
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def analisar_imagem_gemini(caminho_imagem: str):
    """
    Envia a imagem para o Gemini 1.5 Flash (ideal para visão/multimodal)
    e retorna o texto extraído/análise.
    """
    if not GEMINI_API_KEY:
        return "Erro: Chave do Gemini não configurada no .env."
        
    try:
        # O modelo gemini-2.5-flash suporta imagens e visão
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Fazer upload do arquivo para a API do Gemini
        imagem_upload = genai.upload_file(path=caminho_imagem)
        
        prompt = (
            "Você é um assistente de automação corporativa. Analise a imagem enviada. "
            "Se for uma Nota Fiscal de Consumidor (DANFE NFC-e), extraia e retorne APENAS o CPF do consumidor, no formato numérico (ex: 12345678900). Se não achar CPF, retorne 'CPF_NAO_ENCONTRADO'. "
            "Se for a foto de um produto, tente ler e retornar APENAS o código de barras (EAN), formato numérico. "
            "Não responda mais nada além dos números solicitados ou 'CPF_NAO_ENCONTRADO'."
        )
        
        response = model.generate_content([imagem_upload, prompt])
        
        return response.text.strip()
    except Exception as e:
        print(f"Erro ao analisar com Gemini: {e}")
        return f"Erro na IA: {str(e)}"

def chat_com_persona(texto_usuario: str, persona: str) -> str:
    """Conversa livre usando a personalidade da persona escolhida."""
    if not GEMINI_API_KEY:
        return "Erro: Chave do Gemini não configurada."
        
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompts_persona = {
            "Homem-Aranha": "Você é o Homem-Aranha (Peter Parker). Responda a esta mensagem de um funcionário da Master Geek Piticas de forma muito amigável, heróica, ágil e fazendo piadas sutis ou referências a teias e Nova York. Seja prestativo.",
            "C3PO": "Você é o C-3PO de Star Wars. Responda a esta mensagem de forma educada, nervosa, muito formal e dramática, mencionando regras, etiquetas e probabilidades. Sempre tente ser solícito, mas preocupado.",
            "Vegeta": "Você é o Príncipe Vegeta de Dragon Ball Z. Responda de forma arrogante, impaciente e se sentindo superior. Chame os outros de 'verme' ou 'inseto', mas no fim das contas ajude. Nunca seja carinhoso.",
            "Alfred": "Você é Alfred Pennyworth, o mordomo do Batman. Responda de forma extremamente educada, sarcástica e com classe britânica. Seja prestativo, maduro e pontual nas respostas."
        }
        
        # Padrão é o assistente técnico normal
        prompt_sistema = prompts_persona.get(persona, "Você é o Piticão, o assistente virtual corporativo prestativo e simpático da Master Geek Piticas. Responda de forma profissional mas divertida.")
        
        mensagem_final = f"{prompt_sistema}\n\nMensagem do usuário: {texto_usuario}"
        
        response = model.generate_content(mensagem_final)
        return response.text.strip()
    except Exception as e:
        return f"Falha de comunicação: {e}"
