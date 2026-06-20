import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.supabase_service import supabase

def main():
    url_imagem = "https://tqvjataneiyxgwyigzvp.supabase.co/storage/v1/object/public/produtos/c9d0c5c6e93d4569bc396874ef62e5d2.jpg"
    print("Atualizando produto no banco...")
    
    # Atualizar produto ee59d2c6-e1ef-4d7d-a09b-5e428a35fdb5
    response = supabase.table("produtos").update({"imagem_url": url_imagem}).eq("id", "ee59d2c6-e1ef-4d7d-a09b-5e428a35fdb5").execute()
    print("Atualizado com sucesso!")
            
if __name__ == "__main__":
    main()
