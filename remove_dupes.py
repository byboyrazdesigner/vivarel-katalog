import json
from collections import Counter

with open('assets/products.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

print(f"Onceki toplam: {len(products)}")

# Duplike SKU'lari bul
skus = [p.get('sku') for p in products]
dupes = set(sku for sku, count in Counter(skus).items() if count > 1)

print(f"Duplike SKU sayisi: {len(dupes)}")

# Her SKU'dan sadece ilkini tut
seen = set()
cleaned = []
removed = 0

for p in products:
    sku = p.get('sku')
    if sku in dupes:
        if sku not in seen:
            seen.add(sku)
            cleaned.append(p)
        else:
            removed += 1
            name = p.get('name', '')[:40]
            print(f"  Silindi: {sku} - {name}")
    else:
        cleaned.append(p)

print(f"\nSilinen duplike: {removed}")
print(f"Sonraki toplam: {len(cleaned)}")

# Kaydet
with open('assets/products.json', 'w', encoding='utf-8') as f:
    json.dump(cleaned, f, ensure_ascii=False, indent=2)

print("\nKaydedildi!")
