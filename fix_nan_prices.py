import json
import math
import pandas as pd

# Excel oku
df = pd.read_excel('İNTERAKTİF KATALOG FİYAT LİSTESİ 09.01.2026.xlsx', sheet_name='KATALOG', header=1)

# Excel SKU'lari - tum prefix'leri kaldir ve normalize et
excel_data = {}
for _, row in df.iterrows():
    sku_raw = str(row.get('STOK KODU', '')).strip()
    # Tum prefix'leri kaldir: GF, ZD, LG, YM vs
    sku_clean = sku_raw
    for prefix in ['GF ', 'ZD ', 'LG ', 'YM ', 'GF', 'ZD', 'LG', 'YM']:
        sku_clean = sku_clean.replace(prefix, '')
    sku_clean = sku_clean.replace(' ', '').strip()
    
    if sku_clean and pd.notna(row.get('FİYAT')):
        excel_data[sku_clean] = {
            'price': row.get('FİYAT'),
            'image': str(row.get('GÖRSEL LİNKLERİ')) if pd.notna(row.get('GÖRSEL LİNKLERİ')) else None,
            'name': row.get('ÜRÜN ADI'),
        }

# products.json oku
with open('assets/products.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

# nan fiyatli urunleri duzelt
fixed = 0
for p in products:
    price = p.get('price')
    if price is None or (isinstance(price, float) and math.isnan(price)):
        sku = str(p.get('sku', '')).replace(' ', '')
        # Prefix'leri kaldir
        sku_clean = sku
        for prefix in ['GF', 'ZD', 'LG', 'YM']:
            sku_clean = sku_clean.replace(prefix, '')
        
        if sku_clean in excel_data:
            excel = excel_data[sku_clean]
            p['price'] = excel['price']
            p['price_value'] = excel['price']
            p['price_display'] = f"₺{excel['price']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            
            # Gorsel de ekle eger yoksa
            if not p.get('image') and excel.get('image'):
                p['image'] = excel['image']
            
            print(f"Duzeltildi: {p.get('sku')} -> {excel['price']} TL")
            fixed += 1

print(f"\nToplam duzeltilen: {fixed}")

# Kaydet
with open('assets/products.json', 'w', encoding='utf-8') as f:
    json.dump(products, f, ensure_ascii=False, indent=2)

print("Kaydedildi!")
