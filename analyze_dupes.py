import json
from collections import Counter

with open('assets/products.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

skus = [p.get('sku') for p in products]
dupes = [sku for sku, count in Counter(skus).items() if count > 1]

print('=== TUM DUPLIKE ANALIZI ===')
print()

tam_ayni = []
farkli = []

for sku in dupes:
    matches = [p for p in products if p.get('sku') == sku]
    ref = matches[0]
    ayni_mi = all(
        m.get('name') == ref.get('name') and 
        m.get('price') == ref.get('price') and
        m.get('image') == ref.get('image')
        for m in matches[1:]
    )
    if ayni_mi:
        tam_ayni.append(sku)
    else:
        farkli.append((sku, matches))

print(f'TAM AYNI KAYITLAR (silinebilir): {len(tam_ayni)} adet')
for sku in tam_ayni:
    print(f'   {sku}')

print()
print(f'FARKLI BILGILER (dikkat gerekir): {len(farkli)} adet')
for sku, matches in farkli:
    print(f'\n   {sku}:')
    for m in matches:
        name = m.get('name', '')[:45]
        price = m.get('price', 'N/A')
        print(f'      - {name} | Fiyat: {price}')
