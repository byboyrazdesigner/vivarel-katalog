// /js/network-diagnostic.js — Network ve CORS Tanı

window.NetworkDiag = (function() {
  
  function testEndpoint(url) {
    return fetch(url, { mode: 'cors' })
      .then(r => ({
        url,
        status: r.status,
        ok: r.ok,
        contentType: r.headers.get('content-type')
      }))
      .catch(err => ({
        url,
        error: err.message,
        ok: false
      }));
  }

  async function diagnose() {
    console.log('🔍 [NetworkDiag] Ağ tanısı başlıyor...\n');
    
    const tests = [
      '/assets/products.json',
      '/js/config.js',
      '/js/brands.js',
      '/Markalar/ZoneDenmark/index.html',
      '/css/mobile-fixes.css'
    ];
    
    const results = [];
    
    for (const url of tests) {
      const result = await testEndpoint(url);
      results.push(result);
      
      const status = result.ok ? '✅' : result.error ? '❌' : '⚠️';
      console.log(`${status} ${url}`);
      if (result.error) console.log(`   Error: ${result.error}`);
      if (result.status) console.log(`   Status: ${result.status}`);
    }
    
    console.log('\n📊 Sonuçlar:');
    console.table(results);
    
    // localStorage test
    console.log('\n💾 Storage Test:');
    try {
      localStorage.setItem('__test', '1');
      localStorage.removeItem('__test');
      console.log('✅ localStorage: Kullanılabilir');
    } catch (e) {
      console.warn('⚠️ localStorage: ' + e.message + ' (Private Mode?)');
    }
    
    // User Agent
    console.log('\n📱 Device Info:');
    console.log('UA:', navigator.userAgent);
    console.log('Platform:', navigator.platform);
    console.log('iOS?:', /iPad|iPhone|iPod/.test(navigator.userAgent));
  }

  async function testCORS(url) {
    try {
      const r = await fetch(url, { mode: 'cors' });
      console.log(`✅ CORS OK: ${url} (${r.status})`);
      return true;
    } catch (err) {
      console.error(`❌ CORS BLOCKED: ${url}`);
      console.error('   Error:', err.message);
      return false;
    }
  }

  return {
    diagnose,
    testCORS,
    testEndpoint
  };
})();

// Auto-run on iOS
if (/iPad|iPhone|iPod/.test(navigator.userAgent)) {
  window.addEventListener('DOMContentLoaded', () => {
    console.log('📱 iOS Cihaz Tanındı');
    console.log('🔍 Tanı çalıştırmak için: NetworkDiag.diagnose()');
  });
}
