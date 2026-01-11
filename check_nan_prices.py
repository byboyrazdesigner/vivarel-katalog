import json
import math
import pandas as pd

# Excel oku
df = pd.read_excel('İNTERAKTİF KATALOG FİYAT LİSTESİ 09.01.2026.xlsx', sheet_name='KATALOG', header=1)

# Excel SKU'lari - tum prefix'leri kaldir ve normalize et
excel_data = {}
for _, row in df.iterrows():
    sku_raw = str(row.get('STOK KODU', '')).strip()
    # Tum prefix'leri kaldir: GF, ZD, LG vs
    sku_clean = sku_raw
    for prefix in ['GF ', 'ZD ', 'LG ', 'GF', 'ZD', 'LG']:
        sku_clean = sku_clean.replace(prefix, '')
    sku_clean = sku_clean.replace(' ', '').strip()
    
    if sku_clean and pd.notna(row.get('FİYAT')):
        excel_data[sku_clean] = {
            'price': row.get('FİYAT'),
            'image': row.get('GÖRSEL LİNKLERİ') if pd.notna(row.get('GÖRSEL LİNKLERİ')) else None,
            'name': row.get('ÜRÜN ADI'),
            'original_sku': sku_raw
        }

print(f"Excel'de {len(excel_data)} urun")

# products.json oku
with open('assets/products.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

# nan fiyatli urunleri bul
nan_products = []
for p in products:
    price = p.get('price')
    if price is None or (isinstance(price, float) and math.isnan(price)):
        nan_products.append(p)

print(f"products.json'da nan fiyatli: {len(nan_products)}")
print()

# Eslestir
matched = []
not_matched = []

for p in nan_products:
    sku = str(p.get('sku', '')).replace(' ', '')
    if sku in excel_data:
        matched.append({
            'product': p,
            'excel': excel_data[sku]
        })
    else:
        not_matched.append(p)

print(f"=== ESLESEN (duzeltilecek): {len(matched)} ===")
for m in matched[:15]:
    p = m['product']
    e = m['excel']
    print(f"{p.get('sku')}: {p.get('name', '')[:35]}")
    print(f"  Excel fiyat: {e['price']}")

print()
print(f"=== ESLESMEYEN: {len(not_matched)} ===")
for p in not_matched[:10]:
    print(f"{p.get('sku')}: {p.get('name', '')[:40]}")
