import requests
from io import BytesIO
from PIL import Image
from duckduckgo_search import DDGS

def search_and_standardize_funko_image(query: str) -> bytes:
    """
    Busca uma imagem do Funko na internet (DuckDuckGo Images),
    baixa a primeira imagem encontrada e a padroniza (recorta/redimensiona
    para um quadrado com fundo branco).
    Retorna os bytes da imagem final em formato JPEG.
    """
    try:
        # Busca a imagem
        with DDGS() as ddgs:
            results = list(ddgs.images(f"Funko Pop {query} na caixa original", max_results=1))
            
        if not results:
            print("Nenhuma imagem encontrada para:", query)
            return None
            
        image_url = results[0].get('image')
        if not image_url:
            return None
            
        # Baixa a imagem
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(image_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Abre e padroniza a imagem
        img = Image.open(BytesIO(response.content)).convert("RGB")
        
        # Cria um quadrado com fundo branco
        width, height = img.size
        max_dim = max(width, height)
        
        new_img = Image.new("RGB", (max_dim, max_dim), "white")
        
        # Centraliza a imagem original no quadrado branco
        paste_x = (max_dim - width) // 2
        paste_y = (max_dim - height) // 2
        new_img.paste(img, (paste_x, paste_y))
        
        # Redimensiona para um padrão, ex: 800x800
        new_img = new_img.resize((800, 800), Image.Resampling.LANCZOS)
        
        # Salva em bytes
        output = BytesIO()
        new_img.save(output, format="JPEG", quality=90)
        output.seek(0)
        
        return output.read()
        
    except Exception as e:
        print(f"Erro ao buscar/padronizar imagem do Funko: {e}")
        return None
