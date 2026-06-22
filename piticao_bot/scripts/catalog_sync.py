import os
import sys
import requests
import json
import time

# Adicionar a pasta raiz ao sys.path para importar os services
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.supabase_service import supabase

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def sync_vtex_catalog(loja_nome, base_url, max_pages=10):
    print(f"[{loja_nome}] Iniciando sincronização do catálogo completo...")
    
    produtos_inseridos = 0
    
    for page in range(max_pages):
        from_item = page * 50
        to_item = from_item + 49
        
        url = f"{base_url}/api/catalog_system/pub/products/search?_from={from_item}&_to={to_item}"
        
        try:
            print(f"[{loja_nome}] Buscando itens {from_item} a {to_item}...")
            r = requests.get(url, headers=HEADERS, timeout=15)
            
            if r.status_code not in [200, 206]:
                print(f"[{loja_nome}] Erro na requisição: HTTP {r.status_code}")
                break
                
            dados = r.json()
            if not dados:
                print(f"[{loja_nome}] Fim dos resultados.")
                break
                
            for p in dados:
                id_externo = str(p.get("productId"))
                nome = p.get("productName", "")
                descricao = p.get("description", "")
                
                # Extraindo a categoria baseada na hierarquia VTEX
                categorias = p.get("categories", [])
                categoria_principal = categorias[0] if categorias else "Geral"
                
                # Procurar EAN, Preço e Imagem no primeiro SKU ativo
                ean = None
                preco = 0.0
                imagem_url = None
                
                items = p.get("items", [])
                if items:
                    primeiro_sku = items[0]
                    ean = primeiro_sku.get("ean", "")
                    
                    imagens = primeiro_sku.get("images", [])
                    if imagens:
                        imagem_url = imagens[0].get("imageUrl")
                    
                    sellers = primeiro_sku.get("sellers", [])
                    if sellers:
                        oferta = sellers[0].get("commertialOffer", {})
                        preco = oferta.get("Price", 0.0)
                
                if not ean or ean == "":
                    ean = None
                    
                # Inserir no Supabase
                try:
                    existente = supabase.table("catalogo_fornecedores").select("id").eq("origem", loja_nome).eq("id_externo", id_externo).execute()
                    
                    dados_insercao = {
                        "id_externo": id_externo,
                        "nome": nome,
                        "ean": ean,
                        "preco": preco,
                        "imagem_url": imagem_url,
                        "descricao": descricao,
                        "origem": loja_nome
                    }
                    
                    if existente.data:
                        supabase.table("catalogo_fornecedores").update(dados_insercao).eq("id", existente.data[0]["id"]).execute()
                    else:
                        supabase.table("catalogo_fornecedores").insert(dados_insercao).execute()
                        produtos_inseridos += 1
                        print(f"   [+] Novo: {nome} (R$ {preco}) - {categoria_principal}")
                        
                except Exception as db_err:
                    print(f"   [-] Erro ao salvar {nome}: {db_err}")
            
            time.sleep(1) # Respeitar a API
            
        except Exception as e:
            print(f"[{loja_nome}] Exceção: {e}")
            break
            
    print(f"[{loja_nome}] Sincronização finalizada. {produtos_inseridos} novos produtos adicionados!")

if __name__ == "__main__":
    print("Iniciando Catalog Sync...")
    # Sincroniza Piticas (Vestuário, Acessórios)
    sync_vtex_catalog("PITICAS", "https://www.piticas.com.br", max_pages=10)
    # Sincroniza Zona Criativa (Canecas, Acessórios)
    sync_vtex_catalog("ZONA CRIATIVA", "https://www.zonacriativa.com.br", max_pages=10)
    # Sincroniza Moça do Pop (Funkos Exclusivos)
    sync_vtex_catalog("MOÇA DO POP", "https://www.mocadopop.com.br", max_pages=10)
    print("Sincronização Total Concluída!")
