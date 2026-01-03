#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZONE ürünlerindeki duplikasyonları temizle
"""

import json

print("\n📖 products.json okunuyor...")
with open('assets/products.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

print(f"✅ {len(products)} ürün yüklendi")

# ZONE ürünlerini SKU'ya göre grupla
zone_products = {}
other_products = []
duplicates_removed = 0

for product in products:
    if product.get('brand') == 'ZONE':
        sku = str(product.get('sku', ''))
        if sku in zone_products:
            # Duplikat bulundu
            print(f"  ⚠️  Duplikat siliniyor: {sku} - {product['name'][:40]}")
            duplicates_removed += 1
        else:
            # İlk kez görülüyor, sakla
            zone_products[sku] = product
    else:
        other_products.append(product)

# Yeni product listesi oluştur
new_products = other_products + list(zone_products.values())

print(f"\n✅ {duplicates_removed} duplikat ZONE ürünü silindi")
print(f"✅ Kalan ZONE ürünü: {len(zone_products)}")
print(f"✅ Toplam ürün: {len(new_products)}")

# Backup oluştur
print("\n💾 Backup: assets/products.backup.json")
with open('assets/products.backup.json', 'w', encoding='utf-8') as f:
    json.dump(products, f, ensure_ascii=False, indent=2)

# JSON'u kaydet
print("💾 Güncel: assets/products.json")
with open('assets/products.json', 'w', encoding='utf-8') as f:
    json.dump(new_products, f, ensure_ascii=False, indent=2)

print("\n✅ Duplikatlar temizlendi!")
