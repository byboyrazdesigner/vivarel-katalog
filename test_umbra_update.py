#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Umbra ürünlerine CSV'den görselleri ekle (TEST)
"""

import json
import csv

# CSV'yi oku
print("\n📖 CSV dosyası okunuyor...")
image_map = {}
with open('gorsel_linkleri.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.reader(f, delimiter=';')
    for row in reader:
        if len(row) < 4:
            continue
        
        sku = row[0].strip()
        marka = row[1].strip()
        urun_adi = row[2].strip()
        image_url = row[3].strip()
        
        # UMBRA
        if 'UMBRA' in marka.upper() and sku and image_url:
            # SKU normalizasyonu: "UM 020161-165" → "020161-165" (prefix kaldır)
            sku_normalized = sku.replace('UM ', '').strip()
            image_map[str(sku)] = image_url
            image_map[str(sku_normalized)] = image_url  # Prefix'siz versiyon
            print(f"  ✓ {sku} → {sku_normalized}: {image_url[:50]}...")

print(f"\n✅ {len(image_map)} Umbra ürün resmi bulundu (kayıt: {len(image_map)//2})")

# JSON'u oku
print("\n📖 products.json okunuyor...")
with open('assets/products.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

print(f"✅ {len(products)} ürün yüklendi")

# Sadece Umbra ürünlerine resim ekle
updated_count = 0
not_found = []

for product in products:
    if product.get('brand') == 'Umbra':
        sku = str(product.get('sku', ''))
        if sku in image_map:
            product['image'] = image_map[sku]
            updated_count += 1
            print(f"✅ {sku}: Resim eklendi")
            print(f"   {product['name'][:50]}")
            print(f"   {image_map[sku][:70]}...")
        else:
            not_found.append(f"{sku}: {product['name'][:50]}")

# Eşleşmeyen ürünleri göster
if not_found:
    print(f"\n⚠️  {len(not_found)} ürün CSV'de bulunamadı (ilk 5 örnek):")
    for item in not_found[:5]:
        print(f"   • {item}")

# Backup oluştur
print("\n💾 Backup: assets/products.backup.json")
with open('assets/products.backup.json', 'w', encoding='utf-8') as f:
    json.dump(products, f, ensure_ascii=False, indent=2)

# JSON'u kaydet
print("💾 Güncel: assets/products.json")
with open('assets/products.json', 'w', encoding='utf-8') as f:
    json.dump(products, f, ensure_ascii=False, indent=2)

# Özet
print("\n" + "="*60)
print("✅ UMBRA TEST TAMAMLANDI!")
print("="*60)
print(f"📊 Sonuç:")
print(f"   • CSV'de toplam: {len(image_map)//2} ürün")
print(f"   • JSON'da toplam: {sum(1 for p in products if p.get('brand') == 'Umbra')} ürün")
print(f"   • Resim güncellendi: {updated_count}")
print(f"   • CSV'de bulunamayan: {len(not_found)}")

if len(not_found) > 0:
    print(f"\n⚠️  NOT: CSV'de sadece {len(image_map)//2} Umbra ürünü var,")
    print(f"   JSON'da {sum(1 for p in products if p.get('brand') == 'Umbra')} ürün var.")
    print(f"   Kalan {len(not_found)} ürünün görseli CSV'de yok.")

print("\n🎯 Şimdi Umbra markasını aç ve test et!")
