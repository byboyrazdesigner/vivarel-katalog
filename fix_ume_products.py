#!/usr/bin/env python3
"""
UME serisi ZONE ürünlerini düzeltir:
1. BANYO klasöründen SVG'leri bulur
2. SVG'lerden görsel item ID'lerini çıkarır  
3. products.json'da fiyat ve görsel yollarını günceller
"""

import json
import re
import os
from pathlib import Path

# UME serisi ürün bilgileri (screenshot'tan)
UME_PRODUCTS = {
    # Sıvı Sabunluk – Ume
    "ZD15753": {"name": "Sıvı Sabunluk – Ume", "price": 3382.98, "color": "Black"},
    "ZD30394": {"name": "Sıvı Sabunluk – Ume", "price": 3382.98, "color": "Grey"},
    "ZD15756": {"name": "Sıvı Sabunluk – Ume", "price": 3382.98, "color": "Soft Grey"},
    "ZD30395": {"name": "Sıvı Sabunluk – Ume", "price": 3382.98, "color": "White"},
    "ZD15758": {"name": "Sıvı Sabunluk – Ume", "price": 3382.98, "color": "Eucalyptus Green"},
    "ZD30428": {"name": "Sıvı Sabunluk – Ume", "price": 3382.98, "color": "Olive Green"},
    "ZD30439": {"name": "Sıvı Sabunluk – Ume", "price": 3382.98, "color": "Taupe"},
    "ZD31544": {"name": "Sıvı Sabunluk – Ume", "price": 3382.98, "color": "Terracotta"},
    "ZD31553": {"name": "Sıvı Sabunluk – Ume", "price": 3382.98, "color": "Indigo Blue"},
    
    # Diş Fırçalık – Ume
    "ZD15786": {"name": "Diş Fırçalık – Ume", "price": 1804.88, "color": "Black"},
    "ZD30398": {"name": "Diş Fırçalık – Ume", "price": 1804.88, "color": "Grey"},
    "ZD15789": {"name": "Diş Fırçalık – Ume", "price": 1804.88, "color": "Soft Grey"},
    "ZD30397": {"name": "Diş Fırçalık – Ume", "price": 1804.88, "color": "White"},
    "ZD15786": {"name": "Diş Fırçalık – Ume", "price": 1804.88, "color": "Eucalyptus Green"},
    "ZD30430": {"name": "Diş Fırçalık – Ume", "price": 1804.88, "color": "Olive Green"},
    "ZD30440": {"name": "Diş Fırçalık – Ume", "price": 1804.88, "color": "Taupe"},
    "ZD31544": {"name": "Diş Fırçalık – Ume", "price": 1804.88, "color": "Terracotta"},
    "ZD31553": {"name": "Diş Fırçalık – Ume", "price": 1804.88, "color": "Indigo Blue"},
    
    # Katı Sabunluk – Ume
    "ZD31206": {"name": "Katı Sabunluk – Ume", "price": 1568.73, "color": "Black"},
    "ZD31207": {"name": "Katı Sabunluk – Ume", "price": 1568.73, "color": "Grey"},
    "ZD31208": {"name": "Katı Sabunluk – Ume", "price": 1568.73, "color": "Soft Grey"},
    "ZD31209": {"name": "Katı Sabunluk – Ume", "price": 1568.73, "color": "White"},
    "ZD31859": {"name": "Katı Sabunluk – Ume", "price": 1568.73, "color": "Eucalyptus Green"},
    "ZD31854": {"name": "Katı Sabunluk – Ume", "price": 1568.73, "color": "Olive Green"},
    "ZD31547": {"name": "Katı Sabunluk – Ume", "price": 1568.73, "color": "Taupe"},
    "ZD31546": {"name": "Katı Sabunluk – Ume", "price": 1568.73, "color": "Terracotta"},
    "ZD31555": {"name": "Katı Sabunluk – Ume", "price": 1568.73, "color": "Indigo Blue"},
    
    # Kapaklı Kavanoz – Ume
    "ZD15753": {"name": "Kapaklı Kavanoz – Ume", "price": 2359.65, "color": "Black"},
    "ZD15754": {"name": "Kapaklı Kavanoz – Ume", "price": 2359.65, "color": "Grey"},
    "ZD15756": {"name": "Kapaklı Kavanoz – Ume", "price": 2359.65, "color": "Soft Grey"},
    "ZD15757": {"name": "Kapaklı Kavanoz – Ume", "price": 2359.65, "color": "White"},
    "ZD15758": {"name": "Kapaklı Kavanoz – Ume", "price": 2359.65, "color": "Eucalyptus Green"},
    "ZD30438": {"name": "Kapaklı Kavanoz – Ume", "price": 2359.65, "color": "Olive Green"},
    "ZD30439": {"name": "Kapaklı Kavanoz – Ume", "price": 2359.65, "color": "Taupe"},
    "ZD31548": {"name": "Kapaklı Kavanoz – Ume", "price": 2359.65, "color": "Terracotta"},
    "ZD31554": {"name": "Kapaklı Kavanoz – Ume", "price": 2359.65, "color": "Indigo Blue"},
}

# HTML dosyasından SVG item ID'lerini bul
banyo_html = Path("Markalar/ZONE_DENMARK_BANYO/index.html")
html_content = banyo_html.read_text(encoding='utf-8')

# SKU -> item_ID mapping
sku_to_item = {}
for sku in UME_PRODUCTS.keys():
    # SKU'yu hem boşluklu hem boşluksuz ara
    patterns = [
        rf'ZD\s*{sku[2:]}.*?item_(\d+)',
        rf'{sku}.*?item_(\d+)'
    ]
    for pattern in patterns:
        match = re.search(pattern, html_content)
        if match:
            item_id = match.group(1)
            sku_to_item[sku] = f"item_{item_id}.jpg"
            print(f"✓ {sku} → {sku_to_item[sku]}")
            break

# products.json'ı güncelle
json_path = Path("assets/products.json")
with open(json_path, 'r', encoding='utf-8') as f:
    products = json.load(f)

updated_count = 0
for product in products:
    sku = str(product.get("sku", "")).replace(" ", "")
    if sku in UME_PRODUCTS:
        info = UME_PRODUCTS[sku]
        
        # İsmi güncelle
        if product["name"].startswith("Zone Denmark"):
            product["name"] = info["name"]
        
        # Fiyatı güncelle
        product["price"] = info["price"]
        product["price_value"] = info["price"]
        product["price_display"] = f"₺{info['price']:,.2f}".replace(",", ".")
        
        # Görseli ekle
        if sku in sku_to_item:
            product["image"] = f"Markalar/ZONE_DENMARK_BANYO/assets/images/{sku_to_item[sku]}"
        
        # SKU'yu boşluksuz yap
        product["sku"] = sku
        
        # Desc ekle
        product["desc"] = f"Stoneware / Soft Touch; D 8,3 cm, H 12,8 cm; Hacim: 0,25 L; Renk: {info['color']}; Tasarım: VE2"
        
        updated_count += 1
        print(f"✅ Updated: {sku} - {info['name']} - ₺{info['price']}")

# Kaydet
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(products, f, ensure_ascii=False, indent=2)

print(f"\n🎉 {updated_count} ürün güncellendi!")
