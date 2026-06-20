import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.supabase_service import upload_imagem_produto, supabase

def main():
    img_path = r"C:\Users\c.barbosa.CELLAIRIS\.gemini\antigravity-ide\brain\c9622f51-2d77-45ee-a211-f2dcdda47c4e\uploaded_media_1781920176081.img"
    
    if not os.path.exists(img_path):
        print("Imagem não encontrada no caminho.")
        # Trying the other one
        img_path = r"C:\Users\c.barbosa.CELLAIRIS\.gemini\antigravity-ide\brain\c9622f51-2d77-45ee-a211-f2dcdda47c4e\uploaded_media_1781912375697.img"
        if not os.path.exists(img_path):
            print("Nenhuma imagem encontrada.")
            return

    try:
        with open(img_path, "rb") as f:
            img_bytes = f.read()
            
        print("Fazendo upload da imagem...")
        url_imagem = upload_imagem_produto(img_bytes, "funko_homem_aranha_1526_quiosque.jpg")
        
        if url_imagem:
            print(f"Upload concluído: {url_imagem}")
            print("Atualizando produto no banco...")
            
            # Atualizar produto ee59d2c6-e1ef-4d7d-a09b-5e428a35fdb5
            response = supabase.table("produtos_teste").update({"imagem_url": url_imagem}).eq("id", "ee59d2c6-e1ef-4d7d-a09b-5e428a35fdb5").execute()
            print("Atualizado com sucesso!")
        else:
            print("Falha ao fazer upload.")
            
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    main()
