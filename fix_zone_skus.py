#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZONE DENMARK HTML'lerindeki SKU'ları düzelt
ZD10550 → 10550 (ZD prefix'ini kaldır, çünkü JSON'da sadece rakam var)
"""

import re
import os

html_files = [
    'Markalar/ZONE_DENMARK/index.html',
    'Markalar/ZONE_DENMARK_MUTFAK/index.html',
    'Markalar/ZONE_DENMARK_BANYO/index.html'
]

for html_file in html_files:
    if not os.path.exists(html_file):
        print(f"⚠️  {html_file} bulunamadı")
        continue
    
    print(f"\n📄 {html_file} işleniyor...")
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # SKU'ları bul ve düzelt: sku:'ZD10550' → sku:'10550'
    # Regex: sku:'ZD(\d+)' → sku:'\1'
    updated_content = re.sub(r"sku:'ZD(\d+)'", r"sku:'\1'", content)
    
    # Kaç değişiklik yapıldı?
    matches = re.findall(r"sku:'ZD\d+'", content)
    print(f"  ✅ {len(matches)} SKU düzeltildi")
    
    # Kaydet
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(updated_content)

print("\n✅ Tüm HTML'ler güncellendi!")
print("\nŞimdi test_zone_denmark_update.py çalıştırabilirsin.")
