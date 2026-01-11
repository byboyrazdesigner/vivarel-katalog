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

print(f"Excel'de gorseli olan SKU: {len(excel_images)}")

# products.json'da görseli olmayan ama Excel'de olan urunleri bul
missing = []
for p in products:
    sku = str(p.get('sku', '')).replace(' ', '')
    if not p.get('image') or p.get('image') == '':
        if sku in excel_images:
            missing.append({
                'sku': p.get('sku'),
                'name': p.get('name', '')[:40],
                'excel_image': excel_images[sku]
            })

print(f"\n=== EXCEL'DE GORSEL VAR AMA MODAL'DA YOK: {len(missing)} adet ===\n")
for m in missing[:20]:
    print(f"{m['sku']}: {m['name']}")
    print(f"  {m['excel_image'][:70]}...")
    print()

if len(missing) > 20:
    print(f"... ve {len(missing) - 20} tane daha")
