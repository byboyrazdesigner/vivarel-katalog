#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Le Feu ürünlerini günceller ve marka ismini düzeltir
1. "LeFeu" → "Le Feu" normalize et
2. CSV'den görselleri al
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
        
        # LE FEU FİRES
        if 'LE FEU' in marka.upper() and sku and image_url:
            # SKU normalizasyonu: "LE 800061" → "LE800061" (boşluk kaldır)
            sku_normalized = sku.replace(' ', '')
            image_map[sku] = image_url
            image_map[sku_normalized] = image_url  # Boşluksuz versiyon da
            print(f"  ✓ {sku} → {sku_normalized}: {image_url[:50]}...")

print(f"\n✅ {len(image_map)} Le Feu ürün resmi bulundu\n")

# products.json'ı oku
print("📖 products.json okunuyor...")
with open('assets/products.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

print(f"✅ {len(products)} ürün yüklendi\n")

# Le Feu ürünlerini güncelle
updated = 0
brand_fixed = 0
not_found = []

for product in products:
    # "LeFeu" veya "Le Feu" olan tüm ürünler
    brand = product.get('brand', '')
    if 'LEFEU' in brand.upper().replace(' ', ''):
        # Marka ismini düzelt: "LeFeu" → "Le Feu"
        if product['brand'] != 'Le Feu':
            print(f"🔧 Marka düzeltiliyor: '{product['brand']}' → 'Le Feu'")
            product['brand'] = 'Le Feu'
            brand_fixed += 1
        
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

print(f"\n{'='*60}")
print(f"✅ LE FEU TEST TAMAMLANDI!")
print(f"{'='*60}")
print(f"📊 Sonuç:")
print(f"   • Marka ismi düzeltildi: {brand_fixed} ürün")
print(f"   • Resim güncellendi: {updated}")
print(f"   • CSV'de bulunamayan: {len(not_found)}")

if not_found:
    print(f"\n⚠️  CSV'de bulunamayan SKU'lar:")
    for sku in not_found:
        print(f"   • {sku}")

print(f"\n🎯 Şimdi Le Feu markasını aç ve test et!")
print(f"🔍 Marka çipleri kontrol et - artık tek 'Le Feu' olmalı!")
