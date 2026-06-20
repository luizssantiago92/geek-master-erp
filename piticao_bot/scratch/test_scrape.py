import requests
from bs4 import BeautifulSoup

def test_piticas():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        res = requests.get('https://www.piticas.com.br', headers=headers, timeout=10)
        print("Piticas Status:", res.status_code)
    except Exception as e:
        print("Piticas Error:", e)

def test_zonacriativa():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    try:
        res = requests.get('https://www.zonacriativa.com.br', headers=headers, timeout=10)
        print("Zona Criativa Status:", res.status_code)
    except Exception as e:
        print("Zona Criativa Error:", e)

if __name__ == '__main__':
    test_piticas()
    test_zonacriativa()
