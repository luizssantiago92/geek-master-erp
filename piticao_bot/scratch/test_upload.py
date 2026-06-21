import os, sys, requests
sys.path.append(os.getcwd())
from services.supabase_service import upload_image_to_storage

def test_upload():
    url = "https://funko.com.br/arquivos/ids/187989-1000-1000/Boneco-Funko-Pop--Disney-Toy-Story-5---Jessie-12856.jpg"
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    if r.status_code == 200:
        public_url = upload_image_to_storage(r.content, "test_jessie.jpg")
        print(f"URL: {public_url}")
    else:
        print("Falha ao baixar imagem")

if __name__ == "__main__":
    test_upload()
