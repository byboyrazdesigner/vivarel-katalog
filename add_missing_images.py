import pandas as pd
import json

# Excel'den görselleri oku
df = pd.read_excel('İNTERAKTİF KATALOG FİYAT LİSTESİ 09.01.2026.xlsx', sheet_name='KATALOG', header=1)

# products.json oku
with open('assets/products.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

# Excel'de görseli olan SKU'lari bul
excel_images = {}
for _, row in df.iterrows():
    sku = str(row.get('STOK KODU', '')).strip().replace(' ', '')
    img = row.get('GÖRSEL LİNKLERİ', '')
    if pd.notna(img) and img:
        excel_images[sku] = str(img)

# products.json'da görseli olmayan ama Excel'de olan urunleri guncelle
updated = 0
for p in products:
    sku = str(p.get('sku', '')).replace(' ', '')
    if not p.get('image') or p.get('image') == '':
        if sku in excel_images:
            p['image'] = excel_images[sku]
            print(f"Eklendi: {p.get('sku')} - {p.get('name', '')[:40]}")
            updated += 1

print(f"\nToplam guncellenen: {updated}")

# Kaydet
with open('assets/products.json', 'w', encoding='utf-8') as f:
    json.dump(products, f, ensure_ascii=False, indent=2)

print("Kaydedildi!")
