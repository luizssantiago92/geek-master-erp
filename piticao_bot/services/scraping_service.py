import requests
from playwright.sync_api import sync_playwright
from services.supabase_service import upload_image_to_storage
import urllib.parse
import re
from bs4 import BeautifulSoup
import json

def scrape_funko_product(query: str):
    """
    Busca um produto no site funko.com.br via Playwright e raspa os dados reais.
    Retorna o Nome, Preço, Imagem URL (upada no Supabase) e Descrição.
    Caso falhe (timeout ou produto não encontrado), retorna valores de fallback com imagem vazia.
    """
    query_encoded = urllib.parse.quote(query.lower())
    search_url = f"https://funko.com.br/busca?q={query_encoded}"
    
    # Valores de Fallback (Caso o scraper falhe ou não encontre nada)
    result = {
        "nome": f"FUNKO POP {query.upper()}",
        "is_new": False,
        "preco_base": 0.0,
        "imagem_url": "",
        "imagens_galeria": [],
        "descricao": "Produto em análise. Scraper não conseguiu extrair a descrição completa."
    }
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            print(f"[Scraper] Buscando em: {search_url}")
            page.goto(search_url, wait_until="domcontentloaded")
            
            # Tentar achar o primeiro produto da lista (VTEX classes)
            # Como a estrutura pode variar ou ter anti-bot, usamos timeout reduzido
            try:
                page.wait_for_selector('.vtex-product-summary-2-x-clearLink', timeout=8000)
                first_product_href = page.locator('.vtex-product-summary-2-x-clearLink').first.get_attribute('href')
                
                if first_product_href:
                    product_url = f"https://funko.com.br{first_product_href}"
                    print(f"[Scraper] Produto encontrado, navegando para: {product_url}")
                    page.goto(product_url, wait_until="domcontentloaded")
                    
                    # Extrair informações da página de produto
                    page.wait_for_selector('.vtex-store-components-3-x-productBrand', timeout=8000)
                    
                    nome = page.locator('.vtex-store-components-3-x-productBrand').text_content().strip()
                    if nome:
                        result["nome"] = nome
                    
                    # Preço
                    try:
                        preco_str = page.locator('.vtex-product-price-1-x-currencyContainer').first.text_content().strip()
                        # Limpar "R$ 149,99" -> 149.99
                        preco_limpo = re.sub(r'[^\d,]', '', preco_str).replace(',', '.')
                        result["preco_base"] = float(preco_limpo)
                    except Exception as e:
                        print(f"[Scraper] Erro ao extrair preço: {e}")
                    
                    # Imagem Principal
                    try:
                        img_src = page.locator('.vtex-store-components-3-x-productImageTag').first.get_attribute('src')
                        if img_src:
                            result["imagem_url"] = img_src
                    except Exception as e:
                        print(f"[Scraper] Erro ao extrair imagem: {e}")
                        
                    # Descrição
                    try:
                        desc = page.locator('.vtex-store-components-3-x-productDescriptionText').text_content().strip()
                        if desc:
                            result["descricao"] = desc
                    except Exception as e:
                        pass
            except Exception as e:
                print(f"[Scraper] Falha ao encontrar o produto na busca ou anti-bot bloqueou: {e}")
                print(f"[Scraper] Acionando Solução Alternativa de Imagens (Bing API Fallback)...")
                try:
                    query_bing = urllib.parse.quote(f"Funko Pop {query} original na caixa")
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
                                    result["imagem_url"] = img_fallback
                                    print(f"[Scraper] Imagem Fallback encontrada: {img_fallback}")
                                    break
                except Exception as ex_bing:
                    print(f"[Scraper] Bing Fallback também falhou: {ex_bing}")
                    
            finally:
                browser.close()
                
    except Exception as e:
        print(f"[Scraper] Erro fatal no Playwright: {e}")
        
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
