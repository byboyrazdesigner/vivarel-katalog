/* iframe-switcher.js - DISABLED - brands.js handles this now (v23) */
(function () {
  console.log('[iframe-switcher] DISABLED - brands.js handles iframe switching');
  
  // Keep empty stub for compatibility
  window.Brands = window.Brands || {};
  window.Brands.go = function(brand) {
    console.log('[iframe-switcher] go() called but disabled, use Brands.select() instead');
  };
})();
