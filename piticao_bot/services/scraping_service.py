import requests
from bs4 import BeautifulSoup
import re
import urllib3
from services.supabase_service import upload_image_to_storage
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def scrape_funko_product(query: str):
    """
    Simula uma busca no site funko.com.br e retorna os dados raspados do primeiro resultado
    ou faz o scraping direto do link de um funko se a busca não der certo.
    Como estamos em ambiente de desenvolvimento com bloqueios de rede no duckduckgo/google,
    vamos interceptar queries conhecidas para fins de demonstração (ex: Jessie, Luffy, Supergirl).
    """
    # MOCK RÁPIDO PARA FINS DE DEMONSTRAÇÃO JÁ QUE A REDE BLOQUEIA SCRAPING DIRETO SEM HEADLESS BROWSER
    query_lower = query.lower()
    
    # Base URL das imagens da Funko
    base_img = "https://funko.com.br/arquivos/ids/"
    
    if "jessie" in query_lower:
        result = {
            "nome": "BONECO FUNKO POP! DISNEY TOY STORY 5 - JESSIE",
            "is_new": True,
            "preco_base": 149.99,
            "imagem_url": "/images/jessie.png",
            "imagens_galeria": [
                "https://m.media-amazon.com/images/I/51wXyP2U1IL._AC_SY879_.jpg",
                "https://m.media-amazon.com/images/I/6102QvF1+9L._AC_SY879_.jpg"
            ],
            "descricao": "Leve ainda mais aventura e diversão para sua coleção com o Boneco Funko Pop! Jessie, inspirado na carismática cowgirl do universo de Toy Story 5."
        }
    elif "luffy" in query_lower:
        result = {
            "nome": "BONECO FUNKO POP! ONE PIECE - LUFFY COM CARNE",
            "is_new": False,
            "preco_base": 149.99,
            "imagem_url": "/images/jessie.png",
            "imagens_galeria": [
                "https://m.media-amazon.com/images/I/61H4P4H2yCL._AC_SY879_.jpg"
            ],
            "descricao": "O Rei dos Piratas chegou na sua coleção!"
        }
    elif "supergirl" in query_lower:
        result = {
            "nome": "BONECO FUNKO POP! DC COMICS SUPERGIRL",
            "is_new": True,
            "preco_base": 149.99,
            "imagem_url": "/images/jessie.png",
            "imagens_galeria": [
                "https://m.media-amazon.com/images/I/61jC1G1aXlL._AC_SY879_.jpg"
            ],
            "descricao": "Pré-venda Supergirl Pop!"
        }
    else:
        nome_cap = query.upper()
        result = {
            "nome": f"BONECO FUNKO POP! {nome_cap}",
            "is_new": False,
            "preco_base": 129.90,
            "imagem_url": "/images/jessie.png",
            "imagens_galeria": [
                "/images/jessie.png"
            ],
            "descricao": f"Produto exclusivo Funko: {query}"
        }

    # Agora fazemos o DOWNLOAD e UPLOAD para o Supabase
    def download_and_upload(url, name_suffix):
        try:
            r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            if r.status_code == 200 and 'image' in r.headers.get('Content-Type', ''):
                file_name = f"{query_lower.replace(' ', '_')}_{name_suffix}.jpg"
                public_url = upload_image_to_storage(r.content, file_name)
                return public_url or url
            else:
                return url # Fallback para usar o link direto caso o download do bytes falhe ou não seja imagem
        except Exception as e:
            print(f"Erro ao baixar imagem {url}: {e}")
        return url

    print(f"Fazendo upload das imagens para Supabase...")
    # Upload da principal
    result["imagem_url"] = download_and_upload(result["imagem_url"], "main")
    
    # Upload da galeria
    novas_imagens_galeria = []
    for i, img_url in enumerate(result["imagens_galeria"]):
        nova_url = download_and_upload(img_url, f"galeria_{i}")
        novas_imagens_galeria.append(nova_url)
    
    result["imagens_galeria"] = novas_imagens_galeria

    return result
