#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEM ürünlerini günceller
CSV: "TEM AERİS DESİNG" → JSON: "tem"
SKU formatı: "ZAAER-ACC-IT-2-0034" (prefix yok)
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
        
        # TEM AERİS DESİNG
        if 'TEM AER' in marka.upper() and sku and image_url:
            # SKU'lar direk kullanılıyor, prefix yok
            image_map[str(sku)] = image_url
            print(f"  ✓ {sku}: {image_url[:50]}...")

print(f"\n✅ {len(image_map)} TEM ürün resmi bulundu\n")

# products.json'ı oku
print("📖 products.json okunuyor...")
with open('assets/products.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

print(f"✅ {len(products)} ürün yüklendi\n")

# TEM ürünlerini güncelle
updated = 0
not_found = []

for product in products:
    brand = product.get('brand', '')
    
    # "tem" olan ürünler (küçük harf)
    if brand.lower() == 'tem':
        sku = str(product.get('sku', '')).strip()
        
        if sku in image_map:
            product['image'] = image_map[sku]
            updated += 1
            print(f"✅ {sku}: Resim eklendi")
            print(f"   {product['name'][:50]}")
            print(f"   {image_map[sku][:70]}...")
        else:
            not_found.append(sku)
            # Sadece ilk 10 "bulunamadı" mesajını yazdır
            if len(not_found) <= 10:
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
print(f"✅ TEM TEST TAMAMLANDI!")
print(f"{'='*60}")
print(f"📊 Sonuç:")
print(f"   • CSV'de toplam: {len(image_map)} ürün")
print(f"   • JSON'da toplam: {updated + len(not_found)} ürün")
print(f"   • Resim güncellendi: {updated}")
print(f"   • CSV'de bulunamayan: {len(not_found)}")

if not_found:
    print(f"\n⚠️  CSV'de bulunamayan SKU'lar ({len(not_found)} adet):")
    for sku in not_found[:10]:
        print(f"   • {sku}")
    if len(not_found) > 10:
        print(f"   ... ve {len(not_found) - 10} tane daha")

print(f"\n🎯 Şimdi TEM markasını aç ve test et!")
