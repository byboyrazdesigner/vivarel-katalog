import json
import re
import os

BASE = '/Users/muratboyraz/Documents/tem_6_kasim/tem_aralik_2025'

# HTML dosyalarından SKU -> (brand, page) mapping oluştur
def extract_skus_from_html(brand_folder):
    html_path = os.path.join(BASE, 'Markalar', brand_folder, 'index.html')
    if not os.path.exists(html_path):
        return {}
    
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    result = {}
    
    # Sayfa başlangıçlarını bul
    page_pattern = re.compile(r'<li class="page"[^>]*data-name="(\d+)"')
    sku_pattern = re.compile(r"sku[=:]['\"]?([A-Za-z0-9\-]+)")
    
    lines = content.split('\n')
    current_page = None
    
    for line in lines:
        page_match = page_pattern.search(line)
        if page_match:
            current_page = int(page_match.group(1))
        
        sku_match = sku_pattern.search(line)
        if sku_match and current_page:
            sku = sku_match.group(1)
            if sku not in result:
                result[sku] = current_page
    
    return result

# 3 Zone katalogdan SKU'ları çıkar
print("HTML'lerden SKU'lar cikartiliyor...")
zone_skus = {}
for brand in ['ZONE_DENMARK', 'ZONE_DENMARK_BANYO', 'ZONE_DENMARK_MUTFAK']:
    skus = extract_skus_from_html(brand)
    for sku, page in skus.items():
        zone_skus[sku] = {'brand': brand, 'page': page}
    print(f"  {brand}: {len(skus)} SKU")

# products.json oku
with open(os.path.join(BASE, 'assets/products.json'), 'r', encoding='utf-8') as f:
    products = json.load(f)

# Duzelt
fixed_count = 0
for p in products:
    sku = p.get('sku', '')
    
    if sku in zone_skus:
        html_brand = zone_skus[sku]['brand']
        html_page = zone_skus[sku]['page']
        
        if p.get('brand') != html_brand or p.get('page') != html_page:
            old_brand = p.get('brand')
            old_page = p.get('page')
            p['brand'] = html_brand
            p['page'] = html_page
            fixed_count += 1
            print(f"Duzeltildi: {sku}")
            print(f"  {old_brand}/{old_page} -> {html_brand}/{html_page}")

print(f"\nToplam duzeltilen: {fixed_count}")

# Kaydet
with open(os.path.join(BASE, 'assets/products.json'), 'w', encoding='utf-8') as f:
    json.dump(products, f, ensure_ascii=False, indent=2)

print("Kaydedildi!")
