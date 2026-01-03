// /js/error-handler.js — iOS hata yakalama
(function(){
  const errors = [];
  
  // Global error handler
  window.addEventListener('error', function(e){
    // resource-1.css CSS dosya yükleme hataları - güvenle yoksay
    if (e.filename && e.filename.includes('resource-1.css')) {
      console.log('[ErrorHandler] resource-1.css CSS dosya uyarısı (göz ardı edildi)');
      return; // Hata sayılmaz
    }
    
    const msg = `[ERROR] ${e.filename}:${e.lineno}:${e.colno} - ${e.message}`;
    console.error(msg);
    errors.push(msg);
    
    // localStorage'a da kaydet
    try {
      const stored = JSON.parse(localStorage.getItem('__errors') || '[]');
      stored.push({ time: new Date().toISOString(), error: msg });
      localStorage.setItem('__errors', JSON.stringify(stored.slice(-10)));
    } catch(_){}
  }, true);
  
  // Unhandled promise rejection
  window.addEventListener('unhandledrejection', function(e){
    const msg = `[PROMISE] ${e.reason}`;
    console.error(msg);
    errors.push(msg);
  });
  
  // Debug fonksiyonu
  window.ErrorReport = {
    getErrors: () => errors,
    clear: () => { errors.length = 0; localStorage.removeItem('__errors'); },
    log: () => { console.table(errors); }
  };
  
  console.log('[ErrorHandler] Aktif - Hataları görmek için: ErrorReport.log()');
})();
