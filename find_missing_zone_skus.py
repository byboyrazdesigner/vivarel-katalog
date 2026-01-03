#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zone Denmark Banyo'daki ürünleri products.json ile karşılaştır
"""

import json
import re
from pathlib import Path

def find_missing_skus():
    """HTML'deki SKU'ları products.json ile karşılaştır"""
    
    # HTML'den SKU'ları çek
    html_file = Path("/Users/muratboyraz/Downloads/online_catalog/Markalar/ZONE_DENMARK_BANYO/index.html")
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    html_skus = set(re.findall(r"sku:'(ZD\d+)'", html_content))
    print(f"📄 HTML'de {len(html_skus)} benzersiz SKU bulundu")
    
    # products.json'dan ZONE SKU'larını çek
    json_file = Path("/Users/muratboyraz/Downloads/online_catalog/assets/products.json")
    with open(json_file, 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    zone_skus = {str(p['sku']) for p in products if p.get('brand') == 'ZONE' and str(p['sku']).startswith('ZD')}
    print(f"📦 products.json'da {len(zone_skus)} ZONE SKU var")
    
    # Eksik SKU'ları bul
    missing = sorted(html_skus - zone_skus)
    existing = sorted(html_skus & zone_skus)
    
    print(f"\n✅ Mevcut: {len(existing)} SKU")
    print(f"❌ Eksik: {len(missing)} SKU")
    
    if missing:
        print(f"\n🔍 Eksik SKU'lar (ilk 20):")
        for sku in missing[:20]:
            print(f"   - {sku}")
        
        if len(missing) > 20:
            print(f"   ... ve {len(missing) - 20} tane daha")
    
    return missing, html_skus, zone_skus

if __name__ == "__main__":
    find_missing_skus()
