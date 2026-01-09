#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Studio Round Marka Güncellemesi
- StudioGround HTML'ine grid sayfaları ekle (370, 371, 372)
- products.json'a ürünleri ekle
- config.js'deki BRAND_ORDER'u güncelle
"""

import pandas as pd
import json
import re
from datetime import datetime

# ========== YAPILANDIRMA ==========
BRAND_NAME = "STUDIO_ROUND"
BRAND_DISPLAY = "STUDIO ROUND"
FOLDER_NAME = "StudioGround"
START_PAGE = 370  # Grid sayfaları 370'den başlar
PRODUCTS_PER_PAGE = 6

# ========== ÜRÜN BİLGİLERİNİ PARSE ET ==========
def parse_product_name(full_name):
    """Ürün isminden Ölçü, Renk, Malzeme ayır"""
    full_name = str(full_name).strip()
    
    # Ölçü pattern'leri
    olcu = ""
    olcu_patterns = [
        r'Çap:\s*\d+\s*Cm',
        r'\d+\s*[Xx]\s*\d+\s*Cm',
        r'\d+\s*Parça',
    ]
    for pattern in olcu_patterns:
        match = re.search(pattern, full_name, re.IGNORECASE)
        if match:
            olcu = match.group().strip()
            break
    
    # Renk pattern'leri
    renk = ""
    renk_patterns = [
        r'Mat Beyaz/Parlak \w+',
        r'Mat Beyaz/Mat \w+',
        r'Bal Rengi',
    ]
    for pattern in renk_patterns:
        match = re.search(pattern, full_name, re.IGNORECASE)
        if match:
            renk = match.group().strip()
            break
    
    # Malzeme tespiti
    malzeme = ""
    if "Seramik" in full_name:
        malzeme = "Seramik"
    elif "Paslanmaz Çelik" in full_name:
        malzeme = "Paslanmaz Çelik"
    
    # İsmi temizle
    clean_name = full_name
    for pattern in olcu_patterns + renk_patterns:
        clean_name = re.sub(pattern, '', clean_name, flags=re.IGNORECASE)
    clean_name = ' '.join(clean_name.split())
    
    # Kısa isim al
    if len(clean_name) > 40:
        words = clean_name.split()
        short_name = ' '.join(words[:5])
    else:
        short_name = clean_name
    
    return short_name, olcu, renk, malzeme

# ========== EXCEL'DEN ÜRÜNLERI OKU ==========
print("Excel dosyası okunuyor...")
excel_file = "İNTERAKTİF KATALOG FİYAT LİSTESİ 09.01.2026.xlsx"
df = pd.read_excel(excel_file, sheet_name='KATALOG', header=1)

# STUDİO ROUND ürünlerini filtrele
df_sr = df[df['MARKA'] == 'STUDİO ROUND'].copy()
df_sr = df_sr[df_sr['STOK KODU'].notna() & (df_sr['STOK KODU'] != '')]

print(f"Toplam {len(df_sr)} ürün bulundu")

# Ürünleri işle
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
        'full_name': full_name,
        'olcu': olcu,
        'renk': renk,
        'malzeme': malzeme,
        'price': price,
        'price_display': f"₺{price:,.2f}".replace(",", "."),
        'image': image if image and image != 'nan' else ""
    })

print(f"\n{len(products)} ürün hazırlandı:")
for p in products:
    specs = []
    if p['olcu']: specs.append(p['olcu'])
    if p['renk']: specs.append(p['renk'])
    if p['malzeme']: specs.append(p['malzeme'])
    spec_line = " | ".join(specs) if specs else ""
    print(f"  {p['sku']}: {p['name'][:30]}... - {spec_line}")

# ========== PRODUCTS.JSON GÜNCELLE ==========
print("\n\nproducts.json güncelleniyor...")
with open('assets/products.json', 'r', encoding='utf-8') as f:
    all_products = json.load(f)

# Mevcut STUDIO_ROUND ürünlerini sil
original_count = len(all_products)
all_products = [p for p in all_products if p.get('brand') != BRAND_NAME]
removed = original_count - len(all_products)
print(f"  {removed} mevcut {BRAND_NAME} ürünü silindi")

# Yeni ürünleri ekle
for p in products:
    specs = []
    if p['olcu']: specs.append(f"Ölçü: {p['olcu']}")
    if p['renk']: specs.append(f"Renk: {p['renk']}")
    if p['malzeme']: specs.append(f"Malzeme: {p['malzeme']}")
    
    product_entry = {
        "sku": p['sku'],
        "name": p['name'],
        "brand": BRAND_NAME,
        "price": p['price'],
        "price_display": p['price_display'],
        "image": p['image'],
        "specs": " | ".join(specs) if specs else "",
        "full_name": p['full_name']
    }
    all_products.append(product_entry)

print(f"  {len(products)} yeni {BRAND_NAME} ürünü eklendi")
print(f"  Toplam ürün sayısı: {len(all_products)}")

# Kaydet
with open('assets/products.json', 'w', encoding='utf-8') as f:
    json.dump(all_products, f, ensure_ascii=False, indent=2)
print("  products.json kaydedildi!")

# ========== HTML GRİD SAYFALARI OLUŞTUR ==========
print("\n\nHTML grid sayfaları oluşturuluyor...")

# CSS stili
css_style = '''
<!-- Studio Round Grid CSS -->
<style>
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
  font-size: 8px;
  color: #666;
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.studio-product-sku {
  font-size: 7px;
  color: #888;
  margin-bottom: 4px;
}
.studio-product-footer {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-top: auto;
}
.studio-cart-btn {
  background: #333;
  color: #fff;
  border: none;
  padding: 4px 10px;
  font-size: 8px;
  cursor: pointer;
  flex-shrink: 0;
}
.studio-product-price {
  font-size: 10px;
  font-weight: bold;
  color: #333;
}
</style>
'''

def generate_product_card(p):
    """Tek bir ürün kartı HTML'i oluştur"""
    specs = []
    if p['olcu']: specs.append(f"Ölçü: {p['olcu']}")
    if p['renk']: specs.append(f"Renk: {p['renk']}")
    if p['malzeme']: specs.append(f"Malzeme: {p['malzeme']}")
    spec_line = " | ".join(specs) if specs else ""
    
    return f'''      <div class="studio-product-card">
        <img src="{p['image']}" alt="{p['name']}" class="studio-product-image" onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%22100%22 height=%22100%22><rect fill=%22%23f0f0f0%22 width=%22100%22 height=%22100%22/><text x=%2250%22 y=%2250%22 text-anchor=%22middle%22 dy=%22.3em%22 fill=%22%23999%22 font-size=%2212%22>Görsel Yok</text></svg>'">
        <div class="studio-product-name">{p['name']}</div>
        <div class="studio-product-specs">{spec_line}</div>
        <div class="studio-product-sku">{p['sku']}</div>
        <div class="studio-product-footer">
          <button class="studio-cart-btn" onclick="window.parent.postMessage({{type:'ADD_TO_CART',sku:'{p['sku']}'}},'*')">SEPET</button>
          <span class="studio-product-price">{p['price_display']}</span>
        </div>
      </div>'''

def generate_grid_page(page_products, page_num, is_left_page):
    """Grid sayfası HTML'i oluştur"""
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
print(f"  {num_pages} grid sayfası oluşturulacak (Sayfa {START_PAGE}-{START_PAGE + num_pages - 1})")

grid_pages_html = []
for page_idx in range(num_pages):
    start_idx = page_idx * PRODUCTS_PER_PAGE
    end_idx = min(start_idx + PRODUCTS_PER_PAGE, len(products))
    page_products = products[start_idx:end_idx]
    page_num = START_PAGE + page_idx
    is_left = (page_idx % 2 == 0)
    
    page_html = generate_grid_page(page_products, page_num, is_left)
    grid_pages_html.append(page_html)
    print(f"    Sayfa {page_num}: {len(page_products)} ürün")

# ========== MEVCUT HTML'İ GÜNCELLE ==========
print("\n\nStudioGround/index.html güncelleniyor...")
html_path = f"Markalar/{FOLDER_NAME}/index.html"

with open(html_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

# Duplicate kontrolü - eğer sayfa 370 varsa atla
if 'data-name="370"' in html_content:
    print("  Grid sayfaları zaten mevcut, atlanıyor...")
else:
    # CSS ekle (</head> öncesine)
    if 'studio-product-grid' not in html_content:
        html_content = html_content.replace('</head>', f'{css_style}\n</head>')
        print("  CSS eklendi")
    
    # Grid sayfalarını ekle (son </ul> öncesine)
    # Mevcut sayfalar 350-369 arası, biz 370'den başlayarak ekliyoruz
    all_grid_html = "\n".join(grid_pages_html)
    
    # Son sayfa (369) sonrasına ekle
    # </li> sonrasına ve </ul> öncesine
    last_page_pattern = r'(data-name="369".*?</li>)'
    match = re.search(last_page_pattern, html_content, re.DOTALL)
    
    if match:
        insert_pos = match.end()
        html_content = html_content[:insert_pos] + "\n" + all_grid_html + html_content[insert_pos:]
        print(f"  {num_pages} grid sayfası eklendi (370-{START_PAGE + num_pages - 1})")
    else:
        print("  UYARI: Sayfa 369 bulunamadı, </ul> öncesine ekleniyor")
        html_content = html_content.replace('</ul>', f'{all_grid_html}\n</ul>')

# Kaydet
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html_content)
print(f"  {html_path} kaydedildi!")

# ========== CONFIG.JS GÜNCELLE ==========
print("\n\nconfig.js güncelleniyor...")
config_path = "js/config.js"

with open(config_path, 'r', encoding='utf-8') as f:
    config_content = f.read()

# BRAND_PATHS'e ekle
if BRAND_NAME not in config_content:
    brand_path_line = f'  "{BRAND_NAME}":          "/Markalar/{FOLDER_NAME}/index.html",'
    
    # BRAND_PATHS içine ekle
    config_content = config_content.replace(
        '"ZONE_DENMARK_BANYO":    "/Markalar/ZONE_DENMARK_BANYO/index.html"',
        f'"ZONE_DENMARK_BANYO":    "/Markalar/ZONE_DENMARK_BANYO/index.html",\n{brand_path_line}'
    )
    print(f"  BRAND_PATHS'e {BRAND_NAME} eklendi")

# BRAND_ORDER'a ekle (Rosti'den sonra)
if BRAND_NAME not in config_content or '"STUDIO_ROUND"' not in config_content:
    # Mevcut BRAND_ORDER'u bul ve genişlet
    # Şu an sadece Zone markaları var, tüm listeyi yeniden yazalım
    new_brand_order = '''window.Config.BRAND_ORDER = [
  "ZONE_DENMARK",
  "ZONE_DENMARK_MUTFAK",
  "ZONE_DENMARK_BANYO",
  "GEFU",
  "Yamazaki",
  "Hailo",
  "ARIT",
  "Foppapedretti",
  "Lyngby Glas",
  "BAOLGI",
  "TEM",
  "Rosti",
  "STUDIO_ROUND",
  "Bitz",
  "Gense",
  "Le Feu",
  "Umbra",
  "Villa Collection"
];'''
    
    # Mevcut BRAND_ORDER'u değiştir
    brand_order_pattern = r'window\.Config\.BRAND_ORDER\s*=\s*\[[\s\S]*?\];'
    config_content = re.sub(brand_order_pattern, new_brand_order, config_content)
    print(f"  BRAND_ORDER güncellendi ({BRAND_NAME} Rosti'den sonra)")

# Kaydet
with open(config_path, 'w', encoding='utf-8') as f:
    f.write(config_content)
print(f"  {config_path} kaydedildi!")

# ========== ÖZET ==========
print("\n" + "=" * 60)
print("STUDIO ROUND GÜNCELLEME TAMAMLANDI!")
print("=" * 60)
print(f"  • {len(products)} ürün products.json'a eklendi")
print(f"  • {num_pages} grid sayfası HTML'e eklendi (Sayfa {START_PAGE}-{START_PAGE + num_pages - 1})")
print(f"  • BRAND_ORDER'a STUDIO_ROUND eklendi (Rosti'den sonra)")
print("=" * 60)
