import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

print("Testing search...")
r = requests.get('https://funko.com.br/busca?q=jessie', headers=headers)
print("Search Status:", r.status_code)
if r.status_code == 200:
    soup = BeautifulSoup(r.text, 'html.parser')
    products = soup.find_all('a', href=True)
    for p in products:
        if '/p' in p['href'] and 'jessie' in p['href'].lower():
            print("Found product link:", p['href'])
            break

print("Testing product page...")
url = "https://funko.com.br/boneco-funko-pop-disney-toy-story-jessie-12856/p"
r = requests.get(url, headers=headers)
print("Product Status:", r.status_code)
if r.status_code == 200:
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Try finding Lançamento or Pré-Venda
    tags = soup.find_all('p', class_='vtex-product-highlights-2-x-productHighlightText')
    for tag in tags:
        print("Tag:", tag.text)
        
    title = soup.find('span', class_='vtex-store-components-3-x-productBrand')
    if title: print("Title:", title.text)
    
    price = soup.find('span', class_='vtex-product-price-1-x-sellingPriceValue')
    if price: print("Price:", price.text)
    
    desc = soup.find('div', class_='vtex-store-components-3-x-productDescriptionText')
    if desc: print("Description length:", len(desc.text))
    
    images = soup.find_all('img', class_='vtex-store-components-3-x-productImageTag')
    for img in images:
        print("Image:", img.get('src'))
