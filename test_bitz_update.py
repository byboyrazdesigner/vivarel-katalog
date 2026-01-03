#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bitz ürünlerini günceller
CSV: "BI 11193" → JSON: "11193"
"""

import json
import csv

# CSV'yi oku (delimiter ; olduğu için)
print("📖 CSV okunuyor...")
image_map = {}

with open('gorsel_linkleri.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f, delimiter=';')
    
    for row in reader:
        sku = row.get('STOK KODU', '').strip()
        marka = row.get('MARKA', '').strip()
        image_url = row.get('GÖRSEL LİNKLERİ', '').strip()
        
        # BITZ
        if 'BITZ' in marka.upper() and sku and image_url:
            # SKU normalizasyonu: "BI 11193" → "11193" (prefix kaldır)
            sku_normalized = sku.replace('BI ', '').strip()
            image_map[str(sku)] = image_url
            image_map[str(sku_normalized)] = image_url  # Prefix'siz versiyon
            print(f"  ✓ {sku} → {sku_normalized}: {image_url[:50]}...")

print(f"\n✅ {len(image_map)} Bitz ürün resmi bulundu (kayıt: {len(image_map)//2})\n")

# products.json'ı oku
print("📖 products.json okunuyor...")
with open('assets/products.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

print(f"✅ {len(products)} ürün yüklendi\n")

# Bitz ürünlerini güncelle
updated = 0
not_found = []

for product in products:
    brand = product.get('brand', '')
    
    # "Bitz" olan ürünler
    if 'BITZ' in brand.upper():
        sku = str(product.get('sku', '')).strip()
        
        if sku in image_map:
            product['image'] = image_map[sku]
            updated += 1
            print(f"✅ {sku}: Resim eklendi")
            print(f"   {product['name'][:50]}")
            print(f"   {image_map[sku][:70]}...")
        else:
            not_found.append(sku)
            print(f"⚠️  {sku}: CSV'de bulunamadı - {product['name'][:40]}")

# Backup oluştur
print(f"\n💾 Backup: assets/products.backup.json")
with open('assets/products.backup.json', 'w', encoding='utf-8') as f:
    json.dump(products, f, ensure_ascii=False, indent=2)

# Güncellenmiş JSON'ı kaydet
print(f"💾 Güncel: assets/products.json")
with open('assets/products.json', 'w', encoding='utf-8') as f:
    json.dump(products, f, ensure_ascii=False, indent=2)

csv_count = len([k for k in image_map.keys() if k.startswith('BI')])
print(f"\n{'='*60}")
print(f"✅ BITZ TEST TAMAMLANDI!")
print(f"{'='*60}")
print(f"📊 Sonuç:")
print(f"   • CSV'de toplam: {csv_count} ürün")
print(f"   • JSON'da toplam: {updated + len(not_found)} ürün")
print(f"   • Resim güncellendi: {updated}")
print(f"   • CSV'de bulunamayan: {len(not_found)}")

if not_found:
    print(f"\n⚠️  CSV'de bulunamayan SKU'lar:")
    for sku in not_found:
        print(f"   • {sku}")

print(f"\n🎯 Şimdi Bitz markasını aç ve test et!")
