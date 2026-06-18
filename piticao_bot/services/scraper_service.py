import requests
from bs4 import BeautifulSoup
import urllib.parse

def buscar_foto_profissional(nome_produto: str, marca: str) -> str:
    """
    Tenta buscar uma foto de estúdio do produto através de Web Scraping simples.
    Retorna a URL da imagem se encontrar, ou None se falhar.
    """
    if not nome_produto:
        return None
        
    termo = f"{nome_produto} {marca or ''}".strip()
    query = urllib.parse.quote_plus(termo)
    
    # Vamos tentar fazer uma busca simples no Google Imagens (raspagem básica)
    # Importante: Scraping direto no Google ou e-commerces pode ser bloqueado facilmente.
    # Esta é uma abordagem de "melhor esforço" (Best Effort).
    
    url = f"https://www.google.com/search?q={query}&tbm=isch"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # O Google Images usa várias classes, isso pode mudar.
            # Geralmente as imagens ficam em tags img
            imgs = soup.find_all("img")
            
            # Filtra imagens de fallback do Google e tenta pegar a primeira válida
            for img in imgs:
                src = img.get("src") or img.get("data-src")
                if src and src.startswith("http") and "gstatic" not in src:
                    return src
            
            # Segunda tentativa com gstatic se não achar outra (thumbnail do Google)
            for img in imgs[1:]: # pula a primeira que costuma ser o logo
                src = img.get("src") or img.get("data-src")
                if src and src.startswith("http"):
                    return src
                    
        return None
    except Exception as e:
        print(f"Erro no scraping de imagem: {e}")
        return None
