import requests
import json
import base64
import re
from bs4 import BeautifulSoup

url = 'https://funko.com.br/busca?q=darth+vader'
headers = {'User-Agent': 'Mozilla/5.0'}
r = requests.get(url, headers=headers)

if r.status_code == 200:
    soup = BeautifulSoup(r.text, 'html.parser')
    scripts = soup.find_all('script')
    state_str = ''
    for s in scripts:
        if s.string and '__STATE__' in s.string:
            state_str = s.string
            break
            
    if state_str:
        # Match base64 pattern
        match = re.search(r'__STATE__\s*=\s*JSON\.parse\(atob\(\"(.*?)\"\)\)', state_str)
        if match:
            b64 = match.group(1)
            json_str = base64.b64decode(b64).decode('utf-8')
            state = json.loads(json_str)
            for key, val in state.items():
                if 'Product:' in key and val.get('productName'):
                    print('Product:', val.get('productName'))
                    print('Link:', val.get('linkText'))
                    print('Keys:', val.keys())
                    break
        else:
            print("No base64 match, trying raw json")
            match = re.search(r'__STATE__\s*=\s*({.*?});', state_str, re.DOTALL)
            if match:
                print("Found raw json")
                state = json.loads(match.group(1))
                for key, val in state.items():
                    if 'Product:' in key and val.get('productName'):
                        print('Product:', val.get('productName'))
                        break
