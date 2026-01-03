#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel'den ürün resimlerini products.json'a aktarır
"""

import json
import csv
import sys
from pathlib import Path

def update_products_from_csv(csv_path, products_json_path, output_path=None):
    """
    CSV'den ürün resimlerini okur ve products.json'ı günceller
    
    Args:
        csv_path: Excel'den kaydedilmiş CSV dosyası (SKU, ImageURL sütunları)
        products_json_path: Mevcut products.json dosyası
        output_path: Güncellenmiş JSON'ın kaydedileceği yer (None ise products.json üzerine yazar)
    """
    
    # CSV'yi oku
    print(f"📖 CSV okunuyor: {csv_path}")
    image_map = {}
    name_map = {}
    desc_map = {}
    
    with open(csv_path, 'r', encoding='utf-8-sig') as f:  # UTF-8-BOM desteği
        reader = csv.DictReader(f)
        
        # Sütun adlarını kontrol et
        headers = reader.fieldnames
        print(f"📋 CSV sütunları: {headers}")
        
        # SKU ve Image sütunlarını esnek bul
        sku_col = None
        image_col = None
        name_col = None
        desc_col = None
        
        for h in headers:
            h_lower = h.lower().strip()
            if 'sku' in h_lower or 'kod' in h_lower or 'code' in h_lower:
                sku_col = h
            elif 'image' in h_lower or 'resim' in h_lower or 'gorsel' in h_lower or 'url' in h_lower or 'foto' in h_lower:
                image_col = h
            elif 'name' in h_lower or 'ad' in h_lower or 'isim' in h_lower:
                name_col = h
            elif 'desc' in h_lower or 'aciklama' in h_lower or 'tanim' in h_lower:
                desc_col = h
        
        if not sku_col:
            print("❌ HATA: SKU sütunu bulunamadı! (sku, kod, code içeren bir sütun olmalı)")
            print(f"   Mevcut sütunlar: {headers}")
            return False
            
        if not image_col:
            print("❌ HATA: Image sütunu bulunamadı! (image, resim, url içeren bir sütun olmalı)")
            print(f"   Mevcut sütunlar: {headers}")
            return False
        
        print(f"✅ SKU sütunu: '{sku_col}'")
        print(f"✅ Image sütunu: '{image_col}'")
        if name_col:
            print(f"✅ Name sütunu: '{name_col}'")
        if desc_col:
            print(f"✅ Description sütunu: '{desc_col}'")
        
        # Verileri oku
        for row in reader:
            sku = str(row.get(sku_col, '')).strip()
            image_url = str(row.get(image_col, '')).strip()
            
            if sku and image_url:
                # SKU normalizasyonu (boşluk, büyük/küçük harf)
                sku_normalized = sku.strip()
                image_map[sku_normalized] = image_url
                
                # İsteğe bağlı: Name ve Description
                if name_col and row.get(name_col):
                    name_map[sku_normalized] = str(row.get(name_col)).strip()
                if desc_col and row.get(desc_col):
                    desc_map[sku_normalized] = str(row.get(desc_col)).strip()
    
    print(f"✅ {len(image_map)} ürün resmi CSV'den okundu\n")
    
    # products.json'ı oku
    print(f"📖 products.json okunuyor: {products_json_path}")
    with open(products_json_path, 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    print(f"✅ {len(products)} ürün yüklendi\n")
    
    # Güncelleme istatistikleri
    updated_count = 0
    name_updated = 0
    desc_updated = 0
    not_found = []
    
    # Her ürünü güncelle
    for product in products:
        sku = str(product.get('sku', '')).strip()
        
        if sku in image_map:
            # Resim URL'sini güncelle
            old_image = product.get('image')
            new_image = image_map[sku]
            
            product['image'] = new_image
            updated_count += 1
            
            if old_image != new_image:
                print(f"✅ {sku}: Resim güncellendi")
                if old_image:
                    print(f"   Eski: {old_image[:60]}...")
                print(f"   Yeni: {new_image[:60]}...")
            
            # İsteğe bağlı: Name güncelle
            if sku in name_map:
                old_name = product.get('name')
                new_name = name_map[sku]
                if old_name != new_name:
                    product['name'] = new_name
                    name_updated += 1
                    print(f"   📝 Name güncellendi: {new_name[:40]}...")
            
            # İsteğe bağlı: Description güncelle
            if sku in desc_map:
                old_desc = product.get('desc') or product.get('description')
                new_desc = desc_map[sku]
                if old_desc != new_desc:
                    product['desc'] = new_desc
                    product['description'] = new_desc
                    desc_updated += 1
                    print(f"   📝 Description güncellendi: {new_desc[:40]}...")
        else:
            # CSV'de olmayan ürünler
            if product.get('sku'):
                not_found.append(sku)
    
    # Sonuçları kaydet
    output = output_path or products_json_path
    backup_path = products_json_path.replace('.json', '.backup.json')
    
    # Backup oluştur
    print(f"\n💾 Backup oluşturuluyor: {backup_path}")
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    # Güncellenmiş JSON'ı kaydet
    print(f"💾 Güncellenmiş JSON kaydediliyor: {output}")
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    # İstatistikler
    print(f"\n{'='*60}")
    print(f"✅ TAMAMLANDI!")
    print(f"{'='*60}")
    print(f"📊 İstatistikler:")
    print(f"   • Toplam ürün: {len(products)}")
    print(f"   • Resim güncellendi: {updated_count}")
    print(f"   • Name güncellendi: {name_updated}")
    print(f"   • Description güncellendi: {desc_updated}")
    print(f"   • CSV'de bulunamayan: {len(not_found)}")
    
    if not_found and len(not_found) <= 20:
        print(f"\n⚠️  CSV'de bulunamayan SKU'lar:")
        for sku in not_found[:20]:
            print(f"   • {sku}")
    
    print(f"\n💾 Backup: {backup_path}")
    print(f"💾 Güncel: {output}")
    
    return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Kullanım:")
        print("  python3 update_images_from_csv.py <excel_csv_dosyasi>")
        print("")
        print("Örnek:")
        print("  python3 update_images_from_csv.py urun_resimleri.csv")
        print("")
        print("CSV Format:")
        print("  SKU,ImageURL")
        print("  LE 800061,https://example.com/image1.jpg")
        print("  ZD10913,https://example.com/image2.jpg")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    products_file = 'assets/products.json'
    
    if not Path(csv_file).exists():
        print(f"❌ HATA: CSV dosyası bulunamadı: {csv_file}")
        sys.exit(1)
    
    if not Path(products_file).exists():
        print(f"❌ HATA: products.json bulunamadı: {products_file}")
        sys.exit(1)
    
    success = update_products_from_csv(csv_file, products_file)
    sys.exit(0 if success else 1)
