#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON'daki ZONE SKU'larını düzelt
"ZD 332094" → "332094" (ZD ve boşluk kaldır, çünkü HTML'de sadece rakam var)
"ZD25936" → "ZD25936" (boşluksuz olanlar olduğu gibi kalsın)
"""

import json

print("\n📖 products.json okunuyor...")
with open('assets/products.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

print(f"✅ {len(products)} ürün yüklendi")

# ZONE ürünlerinin SKU'larını düzelt
updated_count = 0

for product in products:
    if product.get('brand') == 'ZONE':
        sku = str(product.get('sku', ''))
        
        # "ZD 332094" → "332094" (ZD boşluk ile başlıyorsa)
        if sku.startswith('ZD '):
            new_sku = sku.replace('ZD ', '').strip()
            print(f"  ✓ {sku} → {new_sku}: {product['name'][:50]}")
            product['sku'] = new_sku
            updated_count += 1

print(f"\n✅ {updated_count} ZONE SKU düzeltildi")

# Backup oluştur
print("\n💾 Backup: assets/products.backup.json")
with open('assets/products.backup.json', 'w', encoding='utf-8') as f:
    json.dump(products, f, ensure_ascii=False, indent=2)

# JSON'u kaydet
print("💾 Güncel: assets/products.json")
with open('assets/products.json', 'w', encoding='utf-8') as f:
    json.dump(products, f, ensure_ascii=False, indent=2)

print("\n✅ JSON güncellendi!")
print("Şimdi test_zone_denmark_update.py'yi tekrar çalıştır.")
