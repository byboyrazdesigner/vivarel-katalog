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
    
    # Satır satır işle
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

print(f"\nToplam HTML'de bulunan Zone SKU: {len(zone_skus)}")

# products.json'dan Zone ürünlerini oku
with open(os.path.join(BASE, 'assets/products.json'), 'r', encoding='utf-8') as f:
    products = json.load(f)

zone_products = [p for p in products if 'ZONE' in p.get('brand', '').upper()]
print(f"products.json'daki Zone urun: {len(zone_products)}")

# Karsilastir
print("\n=== UYUMSUZLUKLAR ===\n")
mismatches = []

for p in zone_products:
    sku = p.get('sku', '')
    json_brand = p.get('brand', '')
    json_page = p.get('page')
    
    if sku in zone_skus:
        html_brand = zone_skus[sku]['brand']
        html_page = zone_skus[sku]['page']
        
        if json_brand != html_brand or json_page != html_page:
            mismatches.append({
                'sku': sku,
                'name': p.get('name', '')[:40],
                'json_brand': json_brand,
                'html_brand': html_brand,
                'json_page': json_page,
                'html_page': html_page
            })

print(f"Toplam uyumsuz kayit: {len(mismatches)}\n")

for m in mismatches[:20]:
    print(f"SKU: {m['sku']}")
    print(f"  Urun: {m['name']}")
    print(f"  JSON:  brand={m['json_brand']}, page={m['json_page']}")
    print(f"  HTML:  brand={m['html_brand']}, page={m['html_page']}")
    print()

if len(mismatches) > 20:
    print(f"... ve {len(mismatches) - 20} tane daha")
