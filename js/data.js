// /js/data.js  — FULL

// Fiyat biçimleyici (TRY)
window.Price = {
  formatTRY: (v) => {
    if (v === null || v === undefined || isNaN(v)) return "";
    return new Intl.NumberFormat("tr-TR", {
      style: "currency",
      currency: "TRY",
      maximumFractionDigits: 2
    }).format(Number(v));
  }
};

(function () {
  // ---- Marka adları için alias eşlemesi
  const alias = (b) => {
    if (!b) return b;
    const t = String(b).trim();
    const map = {
      "ZONE": "ZONE_DENMARK",
      "Zone": "ZONE_DENMARK",
      "ZoneDenmark": "ZONE_DENMARK",
      "Zone Denmark": "ZONE_DENMARK"
    };
    return map[t] || t;
  };

  // ---- Ürünleri yükle + State.products doldur + SKU indeksini kur
  async function loadProducts() {
    try {
      // Cache bypass için timestamp ekle
      const timestamp = new Date().getTime();
      const res = await fetch(`assets/products.json?v=${timestamp}`, { 
        cache: "no-store",
        headers: { 'Cache-Control': 'no-cache, no-store, must-revalidate' }
      });
      
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      }
      
      const raw = await res.json();

      // products.json beklenen alanlar: {brand,name,sku,page,price_value,price_display,desc,id,image}
      const items = (Array.isArray(raw) ? raw : raw.items || []).map(p => {
        const priceNum = p.price_value ?? p.price ?? null;
        const priceTxt = p.price_display ?? (priceNum != null ? Price.formatTRY(priceNum) : "");
        return {
          id: p.id ?? `${p.brand}|${p.sku}`,
          brand: alias(p.brand),
          name: p.name,
          sku: p.sku,
          page: p.page ?? null,
          price: priceNum,
          price_display: priceTxt,
          description: p.desc || p.description || "",
          image: p.image || null  // 🆕 Ürün resmi
        };
      });

      window.State = window.State || {};
      window.State.products = items;
      
      console.log(`✅ [Data] ${items.length} ürün yüklendi`);

      // 🔴 Kritik: ürünler yüklendikten sonra SKU indeksini kur
      window.Data.buildSkuIndex();
    } catch (err) {
      console.error('[Data.loadProducts] HATA:', err.message);
      window.State = window.State || {};
      window.State.products = [];
      throw err; // main.js tarafından yakalanacak
    }
  }

  // ---- Data ad alanı
  window.Data = window.Data || {};
  window.Data.loadProducts = loadProducts;

  // === SKU Normalizasyon & İndeks ===

  // Unicode tire/slash varyantlarını normalize et, TİRE'yi koru! (A-Z0-9-)
  window.Data.normalizeSku = function (s) {
    return String(s || "")
      .replace(/[\u2010-\u2015\u2212]/g, "-") // en/em/figure dash, minus sign → -
      .replace(/\u2215/g, "/")               // division slash → /
      .toUpperCase()
      .replace(/[^A-Z0-9\-]/g, ""); // TİRE'yi KORU!
  };

  // sku alanındaki varyantlardan aday tokenlar çıkar:
  //  - ayraçla böl (virgül, slash, pipe, noktalı virgül)
  //  - ayrıca "HARF+RAKAM" kalıplarını da yakala (BE 4116, BK 8147 gibi)
  window.Data.skuTokensFromProduct = function (p) {
    const rawJoined = [p?.sku, p?.ProductCode, p?.product_code, p?.code]
      .filter(Boolean)
      .join(",");

    const normalized = String(rawJoined || "")
      .replace(/[\u2010-\u2015\u2212]/g, "-")
      .replace(/\u2215/g, "/");

    const splitTokens = normalized
      .split(/[,\u002F|;]+/g) // , / | ;
      .map(t => t.trim())
      .filter(Boolean);

    const groupTokens = (normalized.match(/[A-Z]+\s*\d+/gi) || [])
      .map(t => t.replace(/\s+/g, "")); // "BE 4116" → "BE4116"

    const all = new Set(
      [...splitTokens, ...groupTokens]
        .map(window.Data.normalizeSku)
        .filter(Boolean)
    );
    return Array.from(all);
  };

  // State.products üzerindeki tüm tokenları indeksle
  window.Data.buildSkuIndex = function () {
    const idx = new Map();
    (window.State?.products || []).forEach(p => {
      window.Data.skuTokensFromProduct(p).forEach(tok => {
        if (!idx.has(tok)) idx.set(tok, p);
      });
    });
    window.State = window.State || {};
    window.State.skuIndex = idx;
  };
})();
