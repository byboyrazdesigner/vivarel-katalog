#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZONE DENMARK ürünlerine CSV'den görselleri ekle (TEST)
Banyo ve Mutfak hariç, ana ZONE DENMARK kataloğu
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
        
        # ZONE DENMARK (Hepsi - Banyo, Mutfak dahil)
        if 'ZONE DENMARK' in marka.upper() and sku and image_url:
            # CSV'de: "ZD 25936" (boşluklu) veya "ZD 332038"
            # HTML/JSON'da: "ZD25936" (boşluksuz) veya "332038" (ZD yok)
            # Tüm varyasyonları ekleyelim
            
            image_map[str(sku)] = image_url  # Orijinal: "ZD 25936"
            
            # Boşluksuz: "ZD25936"
            sku_no_space = sku.replace(' ', '')
            image_map[str(sku_no_space)] = image_url
            
            # ZD prefix'siz: "25936" veya "332038"
            sku_no_prefix = sku.replace('ZD ', '').replace('ZD', '').strip()
            image_map[str(sku_no_prefix)] = image_url
            
            print(f"  ✓ {sku} → [{sku_no_space}, {sku_no_prefix}]: {image_url[:50]}...")

print(f"\n✅ {len(set(image_map.values()))} benzersiz ZONE DENMARK ürün görseli hazır")
print(f"✅ {len(image_map)} toplam SKU varyasyonu oluşturuldu")
print("\n⚠️  NOT: JSON'daki SKU'lar DEĞİŞTİRİLMEYECEK, sadece image alanı güncellenecek!")

# JSON'u oku
print("\n📖 products.json okunuyor...")
with open('assets/products.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

print(f"✅ {len(products)} ürün yüklendi")

# Sadece ZONE ürünlerine resim ekle
updated_count = 0
not_found = []

for product in products:
    if product.get('brand') == 'ZONE':
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
    print(f"\n⚠️  {len(not_found)} ürün CSV'de bulunamadı (ilk 10 örnek):")
    for item in not_found[:10]:
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
print("✅ ZONE DENMARK TEST TAMAMLANDI!")
print("="*60)
print(f"📊 Sonuç:")
print(f"   • CSV'de toplam: {len(image_map)//2} ürün")
print(f"   • JSON'da toplam: {sum(1 for p in products if p.get('brand') == 'ZONE')} ürün")
print(f"   • Resim güncellendi: {updated_count}")
print(f"   • CSV'de bulunamayan: {len(not_found)}")

if len(not_found) > 0:
    print(f"\n⚠️  NOT: CSV'de sadece {len(image_map)//2} ZONE DENMARK ürünü var,")
    print(f"   JSON'da {sum(1 for p in products if p.get('brand') == 'ZONE')} ürün var.")
    print(f"   Kalan {len(not_found)} ürünün görseli CSV'de yok veya Banyo/Mutfak kategorisinde.")

print("\n🎯 Şimdi ZONE DENMARK markasını aç ve test et!")
