#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARIT - Yeni Export SKU Analizi
"""

import re
from pathlib import Path

html_file = Path("/Users/muratboyraz/Downloads/online_catalog/Markalar/ARIT/index.html")

with open(html_file, 'r', encoding='utf-8') as f:
    html = f.read()

# Tüm SKU'ları çıkar
skus = re.findall(r"sku:'([^']+)'", html)
unique_skus = sorted(set(skus))

print(f'📦 Yeni ARIT Export - SKU Analizi')
print(f'=' * 50)
print(f'Toplam SKU referansı: {len(skus)}')
print(f'Benzersiz SKU: {len(unique_skus)}')
print()

# Smart quote kontrolü
smart = html.count('\u2019')
print(f'Smart quotes: {smart}')

# Bozuk SKU kontrolü
bozuk = [s for s in unique_skus if ',' in s or len(s) > 30]
print(f'Bozuk SKU: {len(bozuk)}')

# '/' kontrolü
slash = [s for s in unique_skus if '/' in s]
print(f"'/' içeren SKU: {len(slash)}")
print()

print('✅ Tüm SKU\'lar:')
for i, sku in enumerate(unique_skus, 1):
    print(f'   {i:2}. {sku}')
