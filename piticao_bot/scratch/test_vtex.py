import requests
import urllib3
urllib3.disable_warnings()

def test_vtex():
    query = "jessie"
    url = f"https://funko.com.br/api/catalog_system/pub/products/search/?ft={query}"
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    r = requests.get(url, headers=headers, verify=False)
    print("Status:", r.status_code)
    if r.status_code == 200:
        data = r.json()
        if data:
            item = data[0]
            print("Title:", item.get("productName"))
            print("Price:", item.get("items")[0].get("sellers")[0].get("commertialOffer").get("Price"))
            print("Images:")
            for img in item.get("items")[0].get("images"):
                print("-", img.get("imageUrl"))
        else:
            print("No items found.")
            
test_vtex()
