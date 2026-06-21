import os, sys
sys.path.append(os.getcwd())
import uuid
from services.scraping_service import scrape_funko_product
from services.supabase_service import salvar_produto

produtos_para_cadastrar = [
    ("jessie", "Disney", "funko"),
    ("luffy", "One Piece", "funko"),
    ("supergirl", "DC Comics", "funko")
]

for p, franquia, tipo in produtos_para_cadastrar:
    res = scrape_funko_product(p)
    if res:
        produto_db = {
            "nome": f"[TESTE] {res['nome']}",
            "franquia": franquia,
            "preco_base": res["preco_base"],
            "imagem_url": res.get("imagem_url"),
            "ean": str(uuid.uuid4())[:13],
            "descricao": res.get("descricao"),
            "is_new": res.get("is_new", False),
            "imagens_galeria": res.get("imagens_galeria", [])
        }
        salvo = salvar_produto(produto_db)
        print(f"Cadastrado: {produto_db['nome']} -> {salvo}")
