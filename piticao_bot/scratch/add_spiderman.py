import sys
import os

# Adds the piticao_bot root to path so we can import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.search_service import search_and_standardize_funko_image
from services.supabase_service import upload_imagem_produto, adicionar_produto_teste

def main():
    nome_funko = "Homem-Aranha 1526"
    franquia = "Marvel"
    preco = 199.90
    
    print(f"Buscando imagem para '{nome_funko}'...")
    img_bytes = search_and_standardize_funko_image(nome_funko)
    
    if img_bytes:
        print("Imagem encontrada. Fazendo upload...")
        url_imagem = upload_imagem_produto(img_bytes, f"funko_{nome_funko.replace(' ', '_')}.jpg")
    else:
        print("Não foi possível encontrar a imagem.")
        url_imagem = None

    print(f"Adicionando produto '{nome_funko}' ao banco...")
    prod = adicionar_produto_teste("Funko Pop " + nome_funko, franquia, preco, url_imagem)
    
    if prod:
        print("✅ Produto adicionado com sucesso:", prod)
    else:
        print("❌ Falha ao adicionar produto.")

if __name__ == "__main__":
    main()
