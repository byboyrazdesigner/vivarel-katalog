#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sadece ARIT ürünlerini günceller (TEST)
CSV'de ARREDAMENTİ olarak geçiyor
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
        
        # ARREDAMENTİ = ARIT (encoding-safe kontrol)
        if marka and 'ARREDAMENT' in marka.upper() and sku and image_url:
            # SKU normalizasyonu
            sku_clean = sku.replace('AR ', '').strip()
            sku_normalized = sku_clean.replace('/', '-').replace('.', '').replace('  ', ' ')
            
            # Özel durumlar: "AR 2008 ALVARO" -> "2008"
            sku_short = sku_clean.split()[0] if ' ' in sku_clean else sku_clean
            
            # Tüm varyasyonları kaydet ama TAM eşleşmeye öncelik ver
            # Stratejisi: En spesifikten en genele doğru
            variants = [sku, sku_normalized, sku_short, sku_clean]
            for variant in variants:
                if variant not in image_map:  # Sadece yoksa ekle (ilk gelen öncelikli)
                    image_map[variant] = image_url
            
            print(f"  ✓ {sku}: {image_url[:50]}...")

print(f"\n✅ {len(image_map)} ARIT (ARREDAMENTİ) ürün resmi bulundu\n")

# products.json'ı oku
print("📖 products.json okunuyor...")
with open('assets/products.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

print(f"✅ {len(products)} ürün yüklendi\n")

# Sadece ARIT ürünlerini güncelle
updated = 0
not_found = []

for product in products:
    if product.get('brand') == 'ARIT':
        sku = str(product.get('sku', '')).strip()
        
        # Normalizasyon: JSON SKU'yu de temizle
        sku_variants = [
            sku,  # Tam eşleşme önce
        ]
        
        # Varyantlar ekle (ama önce tam eşleşmeyi kontrol et)
        if sku.startswith('AR '):
            sku_no_prefix = sku.replace('AR ', '')
            sku_variants.append(sku_no_prefix)
            # L.B. -> LB dönüşümü
            if 'L.B.' in sku or 'LB' in sku:
                sku_variants.append(sku_no_prefix.replace('L.B.', 'LB'))
                sku_variants.append(sku_no_prefix.replace(' LB', ' L.B.'))
        else:
            # SKU "AR " ile başlamıyorsa (örn: "585"), hem "585" hem "AR 585" dene
            sku_with_prefix = f"AR {sku}"
            sku_variants.append(sku_with_prefix)
        
        # Her varyantı dene (önce tam eşleşme)
        matched = False
        for variant in sku_variants:
            if variant in image_map:
                product['image'] = image_map[variant]
                updated += 1
                matched = True
                match_type = "tam eşleşme" if variant == sku else f"varyant: {variant}"
                print(f"✅ {sku}: Resim eklendi ({match_type})")
                print(f"   {product['name'][:50]}")
                print(f"   {image_map[variant][:70]}...")
                break
        
        if not matched:
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
print(f"✅ ARIT (ARREDAMENTİ) TEST TAMAMLANDI!")
print(f"{'='*60}")
print(f"📊 Sonuç:")
print(f"   • Güncellenen: {updated}")
print(f"   • CSV'de bulunamayan: {len(not_found)}")

if not_found:
    print(f"\n⚠️  CSV'de bulunamayan SKU'lar:")
    for sku in not_found:
        print(f"   • {sku}")

print(f"\n🎯 Şimdi ARIT markasını aç ve test et!")
