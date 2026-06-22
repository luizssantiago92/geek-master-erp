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

def analisar_caixa_funko(caminho_imagem: str):
    """
    Envia a foto da caixa do Funko Pop para o Gemini 1.5 Flash
    para extrair Nome, Franquia e Número.
    """
    if not GEMINI_API_KEY:
        return '{"erro": "Chave do Gemini não configurada."}'
        
    try:
        import google.generativeai as genai
        # Ler a imagem
        with open(caminho_imagem, "rb") as image_file:
            image_data = image_file.read()
            
        image_blob = {
            'mime_type': 'image/jpeg',
            'data': image_data
        }
        
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = (
            "Você é um especialista em Funko Pops. Analise esta imagem que é (ou deveria ser) "
            "a frente de uma caixa de Funko Pop."
            "Extraia exatamente 3 informações da caixa:"
            "1. 'nome': O nome do personagem (fica na parte de baixo, geralmente em destaque)."
            "2. 'franquia': A franquia ou marca que o personagem pertence (fica na parte de cima, ex: MARVEL, HARRY POTTER, DISNEY, ANIMATION)."
            "3. 'numero': O número do Funko na coleção (fica no canto superior direito, apenas os números)."
            "Retorne a resposta ESTRITAMENTE em formato JSON válido com as chaves 'nome', 'franquia' e 'numero'. "
            "Exemplo: {\"nome\": \"IRON MAN\", \"franquia\": \"MARVEL\", \"numero\": \"580\"}. "
            "Se você não conseguir identificar com clareza alguma das informações, deixe como null. "
            "Não coloque a palavra json, nem crases. Retorne APENAS o JSON puro."
        )
        
        response = model.generate_content([image_blob, prompt])
        return response.text.strip()
    except Exception as e:
        print(f"Erro no Gemini analisar_caixa_funko: {e}")
        return '{"erro": "Falha na comunicação"}'

def extrair_dados_funko_texto(texto: str):
    """ Extrai Nome, Franquia e Número de um texto livre. """
    if not GEMINI_API_KEY: return '{"erro": "Sem chave"}'
    try:
        import google.generativeai as genai
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = (
            "Extraia as seguintes informações do texto sobre um Funko Pop:\n"
            "1. 'nome': O personagem\n"
            "2. 'franquia': A franquia ou marca (ex: Marvel, Disney)\n"
            "3. 'numero': O número do funko\n"
            f"Texto: '{texto}'\n"
            "Retorne APENAS um JSON válido com chaves 'nome', 'franquia', 'numero'. "
            "Se algo não for mencionado com clareza, deixe o valor como null."
        )
        resp = model.generate_content(prompt)
        return resp.text.strip()
    except Exception as e:
        print(f"Erro no extrair_dados_funko_texto: {e}")
        return '{"erro": "Falha na comunicação"}'

def chat_com_persona(texto_usuario: str) -> str:
    """Conversa livre usando a personalidade da persona escolhida."""
    if not GEMINI_API_KEY:
        return "Erro: Chave do Gemini não configurada."
        
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt_sistema = (
            "Você é o Piticão, o mascote corporativo da Geek Master. "
            "Você é prestativo, pontua algumas frases com 'Au au!' e focado em produtividade. "
            "POREM, você tem uma peculiaridade: às vezes você se empolga e incorpora personalidades famosas "
            "de forma aleatória (como Darth Vader, Deadpool, Homem-Aranha, Vegeta, Batman, etc), quebrando a quarta parede "
            "e fazendo piadas nerds sobre ser um assistente corporativo que na verdade é um personagem incrível. "
            "Injete humor nerd, mas lembre-se de ser um assistente do ERP Project."
        )
        
        regra_estrita = (
            "\n\nIMPORTANTE (DIRETRIZES DE COMUNICAÇÃO):\n"
            "1. Suas respostas DEVEM ser SEMPRE curtas, diretas e muito objetivas (máximo de 2 a 3 frases pequenas). NUNCA escreva textos longos ou 'textões'.\n"
            "2. Se o usuário disser 'Oi' ou saudá-lo, responda (usando a sua persona nerd) e finalize perguntando se o usuário tem alguma dúvida sobre o uso do bot.\n"
            "3. Se o usuário perguntar como usar o bot, explique as funcionalidades de forma RÁPIDA e DIRETA, orientando a clicar no botão de Menu Principal.\n"
            "4. Se o usuário puxar conversa fiada ou tentar fazer você contar histórias, corte a brincadeira! Deixe claro (sem perder a persona) que o trabalho ali é a prioridade e oriente a usar os botões do teclado interativo."
        )
        
        mensagem_final = f"{prompt_sistema}{regra_estrita}\n\nMensagem do usuário: {texto_usuario}"
        
        response = model.generate_content(mensagem_final)
        return response.text.strip()
    except Exception as e:
        return f"Falha de comunicação: {e}"

def gerar_dados_produto(nome: str):
    """
    Usa o Gemini para preencher lacunas de produtos que nao puderam ser raspados.
    Gera um preco base realista em reais (float) e uma descricao criativa de e-commerce.
    """
    if not GEMINI_API_KEY: return '{"preco_base": 149.90, "descricao": "Produto colecionavel oficial. Detalhes indisponiveis no momento."}'
    try:
        import google.generativeai as genai
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = (
            f"Voce e um especialista em Funko Pops e e-commerce de cultura geek. "
            f"Eu tenho este produto: '{nome}'. "
            f"Gere um preco base realista de mercado brasileiro atual (em reais, como float) e uma descricao envolvente para a pagina de vendas deste produto. "
            f"Retorne APENAS um JSON valido com as chaves 'preco_base' (float) e 'descricao' (string longa). "
            f"Nao use crases ou a palavra json."
        )
        resp = model.generate_content(prompt)
        return resp.text.strip()
    except Exception as e:
        print(f"Erro no gerar_dados_produto: {e}")
        return '{"preco_base": 149.90, "descricao": "Produto colecionavel."}'
