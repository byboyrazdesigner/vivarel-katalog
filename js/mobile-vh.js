(function(){
  let lastHeight = window.innerHeight;
  let timeoutId = null;

  function setVH(){
    const currentHeight = window.innerHeight;
    
    // Sadece gerçek yükseklik değişikliklerinde güncelle (zoom değil)
    if (Math.abs(currentHeight - lastHeight) > 10) {
      const vh = currentHeight * 0.01;
      document.documentElement.style.setProperty('--vh', vh + 'px');
      lastHeight = currentHeight;
    }
  }
  
  // İlk yüklemede çalıştır
  setVH();
  
  // Debounce ile resize event'lerini sınırla (200ms)
  window.addEventListener('resize', function() {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
    
    timeoutId = setTimeout(function() {
      setVH();
    }, 200);
  }, { passive: true });
  
  // visualViewport API varsa onu kullan (daha hassas)
  if (window.visualViewport) {
    window.visualViewport.addEventListener('resize', function() {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
      
      timeoutId = setTimeout(function() {
        setVH();
      }, 200);
    }, { passive: true });
  }
})();
