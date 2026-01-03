// /js/main.js — FULL REPLACE
(function () {
  async function boot() {
    console.log('[main] Boot starting (v23)...');
    
    try {
      // 1) Ürünleri yükle (State.products dolar)
      console.log('[main] Loading products...');
      await Data.loadProducts();
      console.log('[main] Products loaded');

      // 2) Marka çiplerini kur
      console.log('[main] Initializing brands...');
      if (typeof Brands?.init === "function") {
        Brands.init();
      }

      // 3) Sepet rozetini senkronize et
      console.log('[main] Updating cart badge...');
      if (typeof Cart?.updateBadge === "function") {
        Cart.updateBadge();
      }

      // 4) Açılış markası seçimi
      console.log('[main] Selecting initial brand...');
      const products = Array.isArray(State?.products) ? State.products : [];
      const hasZone = products.some(p => p.brand === "ZONE" || p.brand === "ZoneDenmark" || p.brand === "ZONE_DENMARK");

      const firstFromOrder =
        (Config.BRAND_ORDER || []).find(b => products.some(p => p.brand === b));

      const firstBrand = hasZone
        ? (products.find(p => p.brand === "ZONE" || p.brand === "ZoneDenmark" || p.brand === "ZONE_DENMARK")?.brand || "ZONE_DENMARK")
        : (firstFromOrder || products[0]?.brand);

      // 5) UI'ı seçili markayla başlat
      if (firstBrand && typeof Brands?.select === "function") {
        Brands.select(firstBrand);
        console.log('[main] Brand selected:', firstBrand);
      }

      // 6) iframe'den gelen mesajları dinle (SEPET butonu için)
      console.log('[main] Setting up iframe listener...');
      setupIframeListener();
      
      console.log('✅ [main] Boot complete!');
    } catch (err) {
      console.error("[main.boot] Hata:", err);
      const chat = document.getElementById("chatMessages");
      if (chat) {
        chat.insertAdjacentHTML(
          "beforeend",
          `<div class="bg-red-900/40 border border-red-700 text-red-200 rounded p-3">
             Başlangıç sırasında bir hata oluştu. <code>assets/products.json</code> yolunu ve JSON biçimini doğrulayın.
           </div>`
        );
      }
    }
  }

  /**
   * iframe'den gelen postMessage'ları dinle
   * In5 HTML içindeki SEPET butonu için
   */
  function setupIframeListener() {
    console.log('[main] Setting up iframe listener (v25)');
    
    window.addEventListener('message', function(event) {
      // Debug: Tüm mesajları logla
      console.log('[main] Message received:', event.data, 'from:', event.origin);
      
      // Güvenlik kontrolü
      if (!event.data || typeof event.data !== 'object') {
        console.log('[main] Invalid message format, ignoring');
        return;
      }

      const { type, sku } = event.data;

      // InDesign kataloglarından gelen mesajlar (sadece iframe içinden)
      // event.source kontrolü ile iframe'den geldiğinden emin ol
      if ((type === 'add-to-cart' || type === 'addToCart') && sku && event.source !== window) {
        console.log('[main] ✅ Valid addToCart from iframe:', sku);
        
        // Direkt adet seçme modalını aç (showAddProductModal)
        if (typeof Cart?.openModalForProduct === 'function') {
          try {
            Cart.openModalForProduct(sku);
            console.log('✅ [main] Product modal opened for SKU:', sku);
          } catch (err) {
            console.error('❌ [main] Sepet hatası:', err);
            if (typeof Toast?.show === 'function') {
              Toast.show('Ürün eklenirken hata oluştu', 'warn');
            }
          }
        } else {
          console.error('[main] Cart.openModalForProduct not available');
        }
      } else {
        console.log('[main] Message ignored:', { type, sku, isIframe: event.source !== window });
      }
    }, false);
  }

  // Tek seferlik bootstrap
  console.log('[main] Registering DOMContentLoaded listener...');
  document.addEventListener("DOMContentLoaded", function() {
    console.log('[main] DOMContentLoaded fired!');
    boot();
  }, { once: true });
  
  console.log('[main] Script loaded (v23)');
})();
