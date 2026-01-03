#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import csv

# SADECE ekran görüntüsündeki SIYAH renkli Nova One ürünleri
# Bunlar CSV'de mevcut, sadece bunları güncelleyeceğiz
BLACK_NOVA_SKUS = [
    "ZD330160",  # Sıvı Sabunluk – Nova One (Black) - ₺2.985,65
    "ZD330161",  # Diş Fırçalık – Nova One (Black) - ₺1.804,88
    "ZD330099",  # Katı Sabunluk – Nova One (Black) - ₺1.568,73
    "ZD28160",   # Kapaklı Kavanoz – Nova One (Black) - ₺1.966,07
]

def get_csv_images():
    """CSV'den görsel linklerini al"""
    csv_images = {}
    
    with open('gorsel_linkleri.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            sku = row.get('STOK KODU', '').strip().replace(" ", "")
            if sku in BLACK_NOVA_SKUS:
                img_link = row.get('GÖRSEL LİNKLERİ', '').strip()
                if img_link:
                    # Tam path'i al
                    csv_images[sku] = img_link
                    print(f"✓ CSV'den bulundu: {sku} -> {img_link.split('/')[-1]}")
    
    return csv_images

def update_products_json(json_file, csv_images):
    """Sadece siyah Nova One ürünlerini CSV görsellerilyle güncelle"""
    
    with open(json_file, 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    updated_count = 0
    
    for product in products:
        sku = str(product.get("sku", "")).replace(" ", "")
        
        if sku in csv_images:
            # Sadece image field'ını güncelle, diğer her şey aynı kalsın
            product["image"] = csv_images[sku]
            print(f"✅ Güncellendi: {sku} -> {csv_images[sku].split('/')[-1]}")
            updated_count += 1
    
    # Güncellenmiş JSON'ı kaydet
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)
    
    return updated_count

def main():
    json_file = "assets/products.json"
    
    print("📝 CSV'den siyah Nova One görsellerini alıyorum...\n")
    csv_images = get_csv_images()
    
    print(f"\n📊 {len(csv_images)} ürün CSV'de bulundu\n")
    
    print("🔄 Sadece bu ürünlerin görsellerini güncelliyorum...\n")
    updated_count = update_products_json(json_file, csv_images)
    
    print(f"\n🎉 {updated_count} ürünün görseli CSV'den güncellendi!")
    print(f"💾 Değişiklikler {json_file} dosyasına kaydedildi")
    print("\n⚠️  DİKKAT: Diğer renkli Nova One ürünlerine hiç dokunulmadı!")

if __name__ == "__main__":
    main()
