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
    
    print(f"[Scraper] Buscando dados reais na mocadopop.com.br para: {query}")
    try:
        url_busca = f"https://www.mocadopop.com.br/buscar?q={urllib.parse.quote(query)}"
        headers = {"User-Agent": "Mozilla/5.0"}
        r_moca = requests.get(url_busca, headers=headers, timeout=10)
        
        if r_moca.status_code == 200:
            soup = BeautifulSoup(r_moca.text, 'html.parser')
            # Loja Integrada
            products = soup.find_all('div', class_='listagem-item')
            if not products:
                products = soup.find_all('li', class_='listagem-item')
                
            if products:
                first_product = products[0]
                
                # Nome
                name_tag = first_product.find('a', class_='nome-produto')
                if name_tag: result["nome"] = name_tag.text.strip()
                
                # Preço
                price_tag = first_product.find('strong', class_='preco-promocional')
                if not price_tag:
                    price_tag = first_product.find('strong', class_='preco-venda')
                
                if price_tag:
                    # Extrair os números "R$ 139,90" -> 139.90
                    price_str = price_tag.text.replace('R$', '').replace('.', '').replace(',', '.').strip()
                    try:
                        result["preco_base"] = float(price_str)
                    except:
                        pass
                        
                # Imagem
                img_tag = first_product.find('img')
                if img_tag:
                    img_url = img_tag.get('data-src') or img_tag.get('src')
                    if img_url and img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    result["imagem_url"] = img_url
                    
                print(f"[Scraper] Sucesso na Moca do Pop! {result['nome']} - R$ {result['preco_base']}")
                
    except Exception as e:
        print(f"[Scraper] Erro ao buscar na Moça do Pop: {e}")
        
    # Se falhar na Moça do pop (imagem vazia), tenta bing fallback
    if not result["imagem_url"]:
        print("[Scraper] Fallback para Bing Images...")
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
                            if ".png" not in img_fallback and "icon" not in img_fallback.lower():
                                result["imagem_url"] = img_fallback
                                break
        except Exception as ex_bing:
            pass

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
