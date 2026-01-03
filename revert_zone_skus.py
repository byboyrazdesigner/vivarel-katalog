#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZONE DENMARK HTML'lerindeki SKU'ları geri al
10550 → ZD10550 (ZD prefix'ini geri ekle)
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
    
    # SKU'ları geri al: sku:'10550' → sku:'ZD10550'
    # Sadece ZONE SKU'larını değiştir (5 haneli sayılar)
    updated_content = re.sub(r"sku:'(\d{5})'", r"sku:'ZD\1'", content)
    
    # Kaç değişiklik yapıldı?
    matches = re.findall(r"sku:'\d{5}'", content)
    print(f"  ✅ {len(matches)} SKU geri alındı (ZD prefix eklendi)")
    
    # Kaydet
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(updated_content)

print("\n✅ HTML'ler eski haline döndürüldü!")
