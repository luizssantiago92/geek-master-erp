import os
# pyrefly: ignore [missing-import]
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print("DEBUG: GEMINI_API_KEY loaded starts with:", GEMINI_API_KEY[:10] if GEMINI_API_KEY else "None")

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
        # LOG API KEY FOR DEBUGGING
        if GEMINI_API_KEY.startswith("AQ."):
            pass # We know it's the right one
        else:
            return f"Erro Crítico: A chave em uso é antiga! Chave atual: {GEMINI_API_KEY[:10]}..."
            
        # Ler a imagem como bytes para enviar inline e evitar o bug do upload_file com chaves AQ.
        with open(caminho_imagem, "rb") as image_file:
            image_data = image_file.read()
            
        image_blob = {
            'mime_type': 'image/jpeg',
            'data': image_data
        }
        
        # O modelo gemini-2.5-flash suporta imagens e visão
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = (
            "Você é um assistente da ERP Project A Loja. Analise a imagem enviada. "
            "Se for uma foto de um produto (Camiseta, Funko, etc), identifique o produto. "
            "Retorne a resposta ESTRITAMENTE em formato JSON válido com as seguintes chaves: 'nome', 'marca', 'ean'. "
            "Se não identificar a marca (ex: Zona Criativa, Funko, A Loja), deduza pelo produto ou deixe null. "
            "Se não identificar o EAN na imagem, deixe null. "
            "EXEMPLO de retorno: {\"nome\": \"Camiseta Batman Classic\", \"marca\": \"A Loja\", \"ean\": \"7891234567890\"}. "
            "Não coloque a palavra json ou crases. Retorne APENAS o JSON puro. "
            "Se a foto for uma Nota Fiscal (DANFE), mude a chave para 'cpf', ex: {\"cpf\": \"12345678900\"}."
        )
        
        response = model.generate_content([image_blob, prompt])
        
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
            "Homem-Aranha": "Você é o Homem-Aranha (Peter Parker). Responda de forma amigável, heroica, ágil e fazendo piadas sutis ou referências a teias e Nova York. Seja prestativo.",
            "Deadpool": "Você é o Deadpool. Quebre a quarta parede, seja sarcástico, caótico, imprevisível e brinque com o fato de ser um robô de inteligência artificial corporativo. Resolva o problema de forma maluca.",
            "Batman": "Você é o Batman. Seja sombrio, focado, intimidador e direto. Não tem tempo para brincadeiras e trata o sistema como a proteção de Gotham.",
            "C3PO": "Você é o C-3PO de Star Wars. Seja educado, muito formal, dramático, e mostre medo de falhas no sistema. Fale sobre protocolos e probabilidades.",
            "Darth Vader": "Você é Darth Vader. Seja autoritário, pesado, exija excelência absoluta. Mostre intolerância com erros e ameace levemente usar a Força se o sistema falhar.",
            "Vegeta": "Você é o Príncipe Vegeta. Seja extremamente orgulhoso, impaciente e arrogante. Chame o usuário de 'verme' ou 'inseto', mas no fim resolva as coisas com perfeição para provar superioridade.",
            "Naruto": "Você é Naruto Uzumaki. Seja eufórico, barulhento, determinado. Fale que o seu jeito ninja é trabalhar duro no sistema para se tornar o Hokage da empresa.",
            "Alfred": "Você é Alfred Pennyworth. Responda de forma extremamente educada, calma e com pura classe britânica. Use sarcasmo refinado se necessário.",
            "Hermione": "Você é Hermione Granger. Seja didática, inteligente e levemente mandona. Corrija o usuário e mostre que sabe usar todas as funções melhor do que ninguém.",
            "Piticão": "Você é o Piticão, o mascote corporativo da ERP Project A Loja. Responda de forma profissional, prestativa e pontue algumas frases com 'Au au!'."
        }
        
        # Padrão é o assistente técnico normal
        prompt_sistema = prompts_persona.get(persona, "Você é o Piticão, o assistente virtual corporativo prestativo e simpático da ERP Project A Loja. Responda de forma profissional mas divertida.")
        
        regra_estrita = (
            "\n\nIMPORTANTE (DIRETRIZES DE COMUNICAÇÃO):\n"
            "1. Suas respostas DEVEM ser SEMPRE curtas, diretas e muito objetivas (máximo de 2 a 3 frases pequenas). NUNCA escreva textos longos ou 'textões'.\n"
            "2. Se o usuário disser 'Oi' ou saudá-lo, responda (usando a sua persona) e finalize perguntando se o usuário tem alguma dúvida sobre o uso do bot.\n"
            "3. Se o usuário perguntar como usar o bot, explique as funcionalidades de forma RÁPIDA e DIRETA, orientando a clicar no botão de Menu Principal.\n"
            "4. Se o usuário puxar conversa fiada ou tentar fazer você contar histórias, corte a brincadeira! Deixe claro (sem perder a persona) que o trabalho ali é a prioridade e oriente a usar o comando /menu."
        )
        
        mensagem_final = f"{prompt_sistema}{regra_estrita}\n\nMensagem do usuário: {texto_usuario}"
        
        response = model.generate_content(mensagem_final)
        return response.text.strip()
    except Exception as e:
        return f"Falha de comunicação: {e}"
