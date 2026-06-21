import os, sys
sys.path.append(os.getcwd())
from services.supabase_service import supabase

def setup_bucket():
    try:
        # Tenta pegar o bucket
        buckets = supabase.storage.list_buckets()
        bucket_names = [b.name for b in buckets]
        
        if "produtos" not in bucket_names:
            print("Bucket 'produtos' não existe. Criando...")
            supabase.storage.create_bucket("produtos", {"public": True})
            print("Bucket criado com sucesso!")
        else:
            print("Bucket 'produtos' já existe.")
    except Exception as e:
        print(f"Erro ao configurar bucket: {e}")

if __name__ == "__main__":
    setup_bucket()
