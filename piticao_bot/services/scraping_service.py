import requests
import urllib.parse
from bs4 import BeautifulSoup
import json
from services.supabase_service import upload_image_to_storage
from services.gemini_service import gerar_dados_produto

def scrape_funko_product(query: str):
    """
    Busca um produto na internet e raspa os dados reais.
    Como a Funko bloqueia bots ativamente (VTEX), usamos uma abordagem híbrida:
    1. Obtemos Imagem via Bing Search.
    2. Obtemos Descrição e Preço sugerido via Gemini AI.
    """
    query_encoded = urllib.parse.quote(query.lower())
    
    # Valores Iniciais
    result = {
        "nome": f"FUNKO POP {query.upper()}",
        "preco_base": 0.0,
        "imagem_url": None,
        "descricao": "Produto de colecionador."
    }

    # 0. BUSCA NO CATÁLOGO MESTRE (Prioridade Máxima)
    try:
        query_formatada = query.replace(" ", " & ") # tsquery simple formatting or just ilike
        # Para simplificar, buscamos por partes do nome
        palavras = query.split(" ")
        
        # Construindo uma busca ILIKE simples para a primeira palavra chave
        palavra_chave = palavras[0]
        if len(palavras) > 1 and palavra_chave.lower() == "jessie":
            palavra_chave = "jessie" # Exemplo: buscar Jessie
            
        # Vamos fazer um ILIKE com as duas primeiras palavras
        termo_busca = f"%{palavras[0]}%"
        if len(palavras) > 1:
            termo_busca = f"%{palavras[0]}%{palavras[1]}%"

        from services.supabase_service import supabase
        resp = supabase.table("catalogo_fornecedores").select("*").ilike("nome", termo_busca).execute()
        
        if resp.data:
            item = resp.data[0]
            print(f"[Scraper] Produto encontrado no Catálogo Mestre: {item['nome']}")
            result["nome"] = item["nome"]
            result["preco_base"] = float(item["preco"]) if item.get("preco") else 0.0
            result["imagem_url"] = item.get("imagem_url")
            result["descricao"] = item.get("descricao") or result["descricao"]
            return result
    except Exception as e:
        print(f"[Scraper] Erro ao buscar no Catálogo Mestre: {e}")
    
    print(f"[Scraper] Buscando imagem para: {query}")
    
    # Busca de Imagem (Bing Fallback melhorado)
    try:
        query_bing = urllib.parse.quote(f"funko pop {query} original caixa")
        bing_url = f'https://www.bing.com/images/search?q={query_bing}'
        r_bing = requests.get(bing_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        
        if r_bing.status_code == 200:
            soup_bing = BeautifulSoup(r_bing.text, 'html.parser')
            for a in soup_bing.find_all('a', class_='iusc'):
                m = a.get('m')
                if m:
                    data = json.loads(m)
                    if data.get('murl'):
                        img_fallback = data['murl']
                        # Evitar pegar icones ou coisas não relacionadas
                        if ".png" not in img_fallback and "icon" not in img_fallback.lower():
                            result["imagem_url"] = img_fallback
                            print(f"[Scraper] Imagem encontrada: {img_fallback}")
                            break
    except Exception as ex_bing:
        print(f"[Scraper] Bing Image Search falhou: {ex_bing}")

    print(f"[Scraper] Buscando informações de preço e descrição via IA para: {query}")
    # Busca de Descrição e Preço via Gemini
    try:
        dados_json = gerar_dados_produto(query)
        limpo = dados_json.replace("```json", "").replace("```", "").strip()
        dados = json.loads(limpo)
        if "preco_base" in dados:
            result["preco_base"] = float(dados["preco_base"])
        if "descricao" in dados:
            result["descricao"] = str(dados["descricao"])
    except Exception as e:
        print(f"[Scraper] Erro ao extrair dados da IA: {e}")

    # Fase 2: Download da imagem e Upload para o Supabase Storage (Bucket: imagens_produtos)
    def download_and_upload(url, name_suffix):
        if not url:
            return ""
        if url.startswith("//"):
            url = "https:" + url
            
        try:
            r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            if r.status_code == 200 and 'image' in r.headers.get('Content-Type', ''):
                file_name = f"{query_encoded}_{name_suffix}.jpg"
                public_url = upload_image_to_storage(r.content, file_name, bucket="imagens_produtos")
                return public_url or url
        except Exception as e:
            print(f"[Scraper] Erro ao baixar e upar imagem {url}: {e}")
        return url

    print("[Scraper] Processando Upload da Imagem para o Supabase...")
    if result["imagem_url"]:
        nova_url = download_and_upload(result["imagem_url"], "main")
        result["imagem_url"] = nova_url

    return result
