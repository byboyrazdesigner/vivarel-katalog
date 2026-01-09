#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Studio Round Grid Sayfalarını Düzelt
- BAOLGI formatına uygun CSS ve buton yapısı
- Roboto font
- add-to-cart message type
"""

import pandas as pd
import json
import re

# ========== YAPILANDIRMA ==========
BRAND_NAME = "STUDIO_ROUND"
FOLDER_NAME = "StudioGround"
START_PAGE = 370
PRODUCTS_PER_PAGE = 6

# ========== EXCEL'DEN ÜRÜNLERI OKU ==========
print("Excel dosyası okunuyor...")
excel_file = "İNTERAKTİF KATALOG FİYAT LİSTESİ 09.01.2026.xlsx"
df = pd.read_excel(excel_file, sheet_name='KATALOG', header=1)

df_sr = df[df['MARKA'] == 'STUDİO ROUND'].copy()
df_sr = df_sr[df_sr['STOK KODU'].notna() & (df_sr['STOK KODU'] != '')]

print(f"Toplam {len(df_sr)} ürün bulundu")

def parse_product_name(full_name):
    full_name = str(full_name).strip()
    
    olcu = ""
    olcu_patterns = [r'Çap:\s*\d+\s*Cm', r'\d+\s*[Xx]\s*\d+\s*Cm', r'\d+\s*Parça']
    for pattern in olcu_patterns:
        match = re.search(pattern, full_name, re.IGNORECASE)
        if match:
            olcu = match.group().strip()
            break
    
    renk = ""
    renk_patterns = [r'Mat Beyaz/Parlak \w+', r'Mat Beyaz/Mat \w+', r'Bal Rengi']
    for pattern in renk_patterns:
        match = re.search(pattern, full_name, re.IGNORECASE)
        if match:
            renk = match.group().strip()
            break
    
    malzeme = ""
    if "Seramik" in full_name:
        malzeme = "Seramik"
    elif "Paslanmaz Çelik" in full_name:
        malzeme = "Paslanmaz Çelik"
    
    clean_name = full_name
    for pattern in olcu_patterns + renk_patterns:
        clean_name = re.sub(pattern, '', clean_name, flags=re.IGNORECASE)
    clean_name = ' '.join(clean_name.split())
    
    if len(clean_name) > 40:
        words = clean_name.split()
        short_name = ' '.join(words[:5])
    else:
        short_name = clean_name
    
    return short_name, olcu, renk, malzeme

products = []
for i, row in df_sr.iterrows():
    sku = str(row.get('STOK KODU', '')).strip()
    full_name = str(row.get('ÜRÜN ADI', '')).strip()
    price = float(row.get('FİYAT', 0)) if pd.notna(row.get('FİYAT')) else 0
    image = str(row.get('GÖRSEL LİNKLERİ', '')).strip()
    
    if pd.isna(sku) or sku == '' or sku == 'nan':
        continue
    
    short_name, olcu, renk, malzeme = parse_product_name(full_name)
    
    products.append({
        'sku': sku,
        'name': short_name,
        'olcu': olcu,
        'renk': renk,
        'malzeme': malzeme,
        'price': price,
        'price_display': f"₺{price:,.2f}".replace(",", "."),
        'image': image if image and image != 'nan' else ""
    })

print(f"{len(products)} ürün hazırlandı")

# ========== BAOLGI FORMATINDA CSS ==========
css_style = '''
<!-- Studio Round Grid CSS - BAOLGI Formatı -->
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
.studio-product-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  grid-template-rows: repeat(3, 1fr);
  gap: 8px;
  padding: 60px 15px 15px 15px;
  height: 100%;
  box-sizing: border-box;
}
.studio-product-card {
  background: #fff;
  padding: 8px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 100%;
  box-sizing: border-box;
}
.studio-product-image {
  width: 100%;
  height: 130px;
  object-fit: contain;
  object-position: left center;
  margin-bottom: 4px;
}
.studio-product-name {
  font-family: 'Roboto', sans-serif;
  font-size: 9px;
  font-weight: bold;
  color: #333;
  line-height: 1.2;
  margin-bottom: 2px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.studio-product-specs {
  font-family: 'Roboto', sans-serif;
  font-size: 8px;
  color: #666;
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.studio-product-sku {
  font-family: 'Roboto', sans-serif;
  font-size: 7px;
  color: #888;
  margin-bottom: 4px;
}
.studio-product-actions {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-top: auto;
}
.studio-cart-btn {
  background: #333;
  color: #fff;
  border: none;
  padding: 6px 16px;
  font-family: 'Roboto', sans-serif;
  font-size: 8px;
  cursor: pointer;
  flex-shrink: 0;
}
.studio-cart-btn:hover {
  background: #555;
}
.studio-product-price {
  font-family: 'Roboto', sans-serif;
  font-size: 10px;
  font-weight: bold;
  color: #333;
}
</style>
'''

def generate_product_card(p):
    """BAOLGI formatında ürün kartı"""
    specs = []
    if p['olcu']: specs.append(f"Ölçü: {p['olcu']}")
    if p['renk']: specs.append(f"Renk: {p['renk']}")
    if p['malzeme']: specs.append(f"Malzeme: {p['malzeme']}")
    spec_line = " | ".join(specs) if specs else ""
    
    return f'''      <!-- Product: {p['sku']} -->
      <div class="studio-product-card">
        <img src="{p['image']}" alt="{p['name']}" class="studio-product-image" onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%22100%22 height=%22100%22><rect fill=%22%23f0f0f0%22 width=%22100%22 height=%22100%22/><text x=%2250%22 y=%2250%22 text-anchor=%22middle%22 dy=%22.3em%22 fill=%22%23999%22 font-size=%2212%22>Görsel Yok</text></svg>'">
        <div class="studio-product-name">{p['name']}</div>
        <div class="studio-product-specs">{spec_line}</div>
        <div class="studio-product-sku">{p['sku']}</div>
        <div class="studio-product-actions">
          <a href="javascript:window.parent.postMessage({{type:'add-to-cart',sku:'{p['sku']}'}},'*')">
            <button class="studio-cart-btn">SEPET</button>
          </a>
          <span class="studio-product-price">{p['price_display']}</span>
        </div>
      </div>'''

def generate_grid_page(page_products, page_num):
    cards_html = "\n".join([generate_product_card(p) for p in page_products])
    
    return f'''  <li class="page" data-name="{page_num}">
    <div class="page-scale-wrap" style="width:595px;height:842px;position:relative;background:#fff;">
    <div class="studio-product-grid">
{cards_html}
    </div>
    </div>
  </li>'''

# Sayfaları oluştur
num_pages = (len(products) + PRODUCTS_PER_PAGE - 1) // PRODUCTS_PER_PAGE
print(f"{num_pages} grid sayfası oluşturulacak")

grid_pages_html = []
for page_idx in range(num_pages):
    start_idx = page_idx * PRODUCTS_PER_PAGE
    end_idx = min(start_idx + PRODUCTS_PER_PAGE, len(products))
    page_products = products[start_idx:end_idx]
    page_num = START_PAGE + page_idx
    
    page_html = generate_grid_page(page_products, page_num)
    grid_pages_html.append(page_html)
    print(f"  Sayfa {page_num}: {len(page_products)} ürün")

# ========== HTML'İ GÜNCELLE ==========
print("\nStudioGround/index.html güncelleniyor...")
html_path = f"Markalar/{FOLDER_NAME}/index.html"

with open(html_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

# Eski CSS'i kaldır
html_content = re.sub(r'<!-- Studio Round Grid CSS -->.*?</style>\s*', '', html_content, flags=re.DOTALL)
html_content = re.sub(r'<!-- Studio Round Grid CSS - BAOLGI Formatı -->.*?</style>\s*', '', html_content, flags=re.DOTALL)

# Eski grid sayfalarını kaldır (370-372)
html_content = re.sub(r'\s*<li class="page" data-name="37[0-9]">.*?</li>', '', html_content, flags=re.DOTALL)

# Yeni CSS ekle
html_content = html_content.replace('</head>', f'{css_style}\n</head>')
print("  Yeni CSS eklendi")

# Yeni grid sayfalarını ekle
all_grid_html = "\n".join(grid_pages_html)

last_page_pattern = r'(data-name="369".*?</li>)'
match = re.search(last_page_pattern, html_content, re.DOTALL)

if match:
    insert_pos = match.end()
    html_content = html_content[:insert_pos] + "\n" + all_grid_html + html_content[insert_pos:]
    print(f"  {num_pages} grid sayfası eklendi")
else:
    print("  UYARI: Sayfa 369 bulunamadı")

# Kaydet
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"\n✅ {html_path} güncellendi!")
print(f"   - Roboto font eklendi")
print(f"   - BAOLGI formatında butonlar (add-to-cart)")
print(f"   - {num_pages} grid sayfası ({START_PAGE}-{START_PAGE + num_pages - 1})")
