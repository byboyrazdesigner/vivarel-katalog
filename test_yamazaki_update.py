#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Yamazaki ürünlerini günceller
CSV: "YM 2427" → JSON: "2427"
NOT: CSV'de sadece 8 Yamazaki ürünü var, JSON'da 284 ürün var
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
        
        # YAMAZAKİ (Türkçe İ harfi ile)
        if 'YAMAZAK' in marka.upper() and sku and image_url:
            # SKU normalizasyonu: "YM 1460" → "1460" (prefix kaldır)
            sku_normalized = sku.replace('YM ', '').strip()
            image_map[str(sku)] = image_url
            image_map[str(sku_normalized)] = image_url  # Prefix'siz versiyon
            
            # JSON'da SKU'lar "WH1460", "BK1461" gibi renk kodu ile başlıyor
            # Son 4 rakamı eşleştirmek için tüm olası kombinasyonları ekle
            if len(sku_normalized) >= 4:
                # WH (Beyaz), BK (Siyah), BE (Bej), CL (LAYER serisi) gibi prefix'ler ekle
                for prefix in ['WH', 'BK', 'BE', 'BR', 'GR', 'RD', 'CL', 'FL', 'PK', 'NA', 'OR']:
                    sku_with_color = prefix + sku_normalized
                    image_map[str(sku_with_color)] = image_url
            
            print(f"  ✓ {sku} → {sku_normalized} + renk kodları: {image_url[:50]}...")

print(f"\n✅ {len(image_map)} Yamazaki ürün resmi bulundu (kayıt: {len(image_map)//2})\n")

# products.json'ı oku
print("📖 products.json okunuyor...")
with open('assets/products.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

print(f"✅ {len(products)} ürün yüklendi\n")

# Yamazaki ürünlerini güncelle
updated = 0
not_found = []

for product in products:
    brand = product.get('brand', '')
    
    # "Yamazaki" olan ürünler
    if 'YAMAZAKI' in brand.upper():
        sku = str(product.get('sku', '')).strip()
        
        if sku in image_map:
            product['image'] = image_map[sku]
            updated += 1
            print(f"✅ {sku}: Resim eklendi")
            print(f"   {product['name'][:50]}")
            print(f"   {image_map[sku][:70]}...")
        else:
            not_found.append(sku)

# CSV'de bulunmayan ürünleri özetleyerek göster
if not_found:
    print(f"\n⚠️  {len(not_found)} ürün CSV'de bulunamadı (ilk 5 örnek):")
    for sku in not_found[:5]:
        matching_product = next((p for p in products if str(p.get('sku', '')) == sku), None)
        if matching_product:
            print(f"   • {sku}: {matching_product['name'][:40]}")

# Backup oluştur
print(f"\n💾 Backup: assets/products.backup.json")
with open('assets/products.backup.json', 'w', encoding='utf-8') as f:
    json.dump(products, f, ensure_ascii=False, indent=2)

# Güncellenmiş JSON'ı kaydet
print(f"💾 Güncel: assets/products.json")
with open('assets/products.json', 'w', encoding='utf-8') as f:
    json.dump(products, f, ensure_ascii=False, indent=2)

csv_count = len([k for k in image_map.keys() if k.startswith('YM')])
print(f"\n{'='*60}")
print(f"✅ YAMAZAKİ TEST TAMAMLANDI!")
print(f"{'='*60}")
print(f"📊 Sonuç:")
print(f"   • CSV'de toplam: {csv_count} ürün")
print(f"   • JSON'da toplam: {updated + len(not_found)} ürün")
print(f"   • Resim güncellendi: {updated}")
print(f"   • CSV'de bulunamayan: {len(not_found)}")
print(f"\n⚠️  NOT: CSV'de sadece {csv_count} Yamazaki ürünü var,")
print(f"   JSON'da {updated + len(not_found)} ürün var.")
print(f"   Kalan {len(not_found)} ürünün görseli CSV'de yok.")

print(f"\n🎯 Şimdi Yamazaki markasını aç ve test et!")
