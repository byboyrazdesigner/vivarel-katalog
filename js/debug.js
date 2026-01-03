// /js/debug.js — Hata ayıklama ve test araçları

window.Debug = (function() {
  
  function log(category, msg, data = null) {
    const time = new Date().toLocaleTimeString('tr-TR');
    const prefix = `[${time}] [${category}]`;
    if (data) {
      console.log(`%c${prefix} ${msg}`, 'color: #00bfff; font-weight: bold;', data);
    } else {
      console.log(`%c${prefix} ${msg}`, 'color: #00bfff; font-weight: bold;');
    }
  }

  // Sistem durumunu kontrol et
  function checkSystem() {
    console.clear();
    log('DEBUG', '=== SİSTEM KONTROL ===');
    
    // 1. State.products kontrolü
    const productsCount = (window.State?.products || []).length;
    log('STATE', `Ürünler yüklü: ${productsCount}`, window.State?.products?.slice(0, 2));
    
    // 2. iframe kontrolü
    const frame = document.getElementById('brandFrame');
    log('IFRAME', frame ? 'İframe bulundu ✓' : 'İframe BULUNAMADI ✗', frame?.src);
    
    // 3. Marka çipleri
    const chips = document.querySelectorAll('.brand-chip');
    log('CHIPS', `${chips.length} marka çipsi bulundu`, Array.from(chips).map(c => c.textContent));
    
    // 4. Config kontrolü
    log('CONFIG', 'Brand paths:', window.Config.BRAND_PATHS);
    log('CONFIG', 'Brand order:', window.Config.BRAND_ORDER);
    
    // 5. CSS :active desteği
    const supportsActive = CSS.supports('background-color', 'rgb(249, 115, 22)');
    log('CSS', 'Active state desteği: ' + (supportsActive ? '✓' : '⚠'));
    
    // 6. Touch event desteği
    const hasTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    log('TOUCH', 'Touch event desteği: ' + (hasTouch ? '✓' : '✗'));
  }

  // Marka seçimini test et
  function testBrandSelect(brandName) {
    log('TEST', `Marka seçimi test: ${brandName}`);
    if (typeof Brands?.select === 'function') {
      Brands.select(brandName);
      log('TEST', 'Brands.select() çağrıldı');
    } else {
      log('TEST', 'ERROR: Brands.select() bulunamadı!');
    }
  }

  // postMessage dinleyicisini test et
  function testPostMessage() {
    log('TEST', 'postMessage test başlıyor...');
    window.postMessage({ type: 'add-to-cart', sku: 'TEST123' }, '*');
    log('TEST', 'Test mesajı gönderildi');
  }

  // LocalStorage durumunu kontrol et
  function checkStorage() {
    log('STORAGE', '=== STORAGE KONTROL ===');
    
    let canStore = true;
    try {
      localStorage.setItem('__test', '1');
      localStorage.removeItem('__test');
    } catch (e) {
      canStore = false;
      log('STORAGE', 'localStorage KULLANILAMIYOR (Private Mode?)');
    }
    
    if (canStore) {
      const cartData = localStorage.getItem('tem_cart_v1');
      log('STORAGE', 'Sepet verisi:', cartData ? JSON.parse(cartData) : 'Boş');
    }
  }

  // Tüm marka kaynakları kontrol et
  function checkAllBrandSources() {
    log('BRANDS', '=== TÜM MARKA KAYNAKLARI ===');
    const brands = window.Config.BRAND_ORDER || [];
    brands.forEach(brand => {
      const src = window.Config.brandToSrc(brand);
      log('BRANDS', `${brand}:`, src);
    });
  }

  // İframe ile postMessage test
  function testIframePostMessage() {
    log('TEST', 'iframe postMessage testi...');
    const frame = document.getElementById('brandFrame');
    if (!frame) {
      log('TEST', 'ERROR: iframe bulunamadı');
      return;
    }
    
    frame.contentWindow.postMessage({ type: 'test', message: 'Merhaba iframe!' }, '*');
    log('TEST', 'Test mesajı iframe\'e gönderildi');
  }

  // Hızlı test komutu
  function quickTest() {
    console.clear();
    log('QUICK', 'Hızlı test başlıyor...\n');
    
    checkSystem();
    console.log('\n');
    
    checkStorage();
    console.log('\n');
    
    checkAllBrandSources();
    console.log('\n');
    
    log('QUICK', 'Test tamamlandı. Komutlar:');
    console.log(`
    Debug.testBrandSelect('ARIT')
    Debug.testPostMessage()
    Debug.testIframePostMessage()
    Debug.checkStorage()
    Debug.checkAllBrandSources()
    `);
  }

  return {
    log,
    checkSystem,
    testBrandSelect,
    testPostMessage,
    testIframePostMessage,
    checkStorage,
    checkAllBrandSources,
    quickTest
  };
})();

// Sayfa yüklendiğinde otomatik kontrol
document.addEventListener('DOMContentLoaded', () => {
  setTimeout(() => {
    Debug.log('INIT', 'Sayfa tamamen yüklendi');
  }, 1000);
});
