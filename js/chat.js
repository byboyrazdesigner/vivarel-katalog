// /js/chat.js — FULL REPLACE
// Basit chat + arama + kart render + inceleme modalı
// Not: postMessage dinleyicisi YOK. (cart.js tek otorite)

window.Chat = (function () {
  // ---- Toast köprüsü (cart.js’teki Toast varsa onu kullan) ----
  const Toast = (function(){
    if (window.Toast) return window.Toast; // cart.js tanımladıysa kullan
    // Minimal fallback (çok nadir gerekli)
    let stack = null;
    function ensure(){
      if (stack) return;
      stack = document.createElement('div');
      stack.style.cssText = 'position:fixed;right:16px;bottom:16px;z-index:9999;display:flex;flex-direction:column;gap:8px;pointer-events:none';
      document.body.appendChild(stack);
    }
    function show(msg, type='info'){
      ensure();
      const bg     = type==='success' ? '#065f46' : type==='warn' ? '#92400e' : '#374151';
      const border = type==='success' ? '#10b981' : type==='warn' ? '#f59e0b' : '#9ca3af';
      const el = document.createElement('div');
      el.style.cssText = `
        min-width:240px;max-width:90vw;color:#fff;background:${bg};
        border:1px solid ${border};border-radius:10px;padding:10px 12px;
        box-shadow:0 10px 20px rgba(0,0,0,.25);opacity:0;transform:translateY(8px);
        transition:opacity .2s, transform .2s;pointer-events:auto;font-size:13px;line-height:1.35;
      `;
      el.textContent = msg;
      stack.appendChild(el);
      requestAnimationFrame(()=>{ el.style.opacity='1'; el.style.transform='translateY(0)' });
      setTimeout(()=>{
        el.style.opacity='0'; el.style.transform='translateY(8px)';
        setTimeout(()=> el.remove(), 220);
      }, 2400);
    }
    return { show };
  })();

  const elMsgs  = () => document.getElementById('chatMessages');
  const elInput = () => document.getElementById('chatInput');

  // ------------------- UTIL -------------------
  function escapeHTML(t){
    return String(t).replace(/[&<>"']/g, m => ({
      '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
    }[m]));
  }
  function scrollToBottom(){
    const box = elMsgs(); if (box) box.scrollTop = box.scrollHeight;
  }

  // ------------------- CLEAR -------------------
  function clear() {
    if (!confirm('Sohbeti temizlemek istiyor musunuz?')) return;
    const box = elMsgs(); if (!box) return;
    box.innerHTML = `
      <div class="chat-message chat-message-bot">
        <p class="text-sm text-gray-200 leading-relaxed">
          👋 Merhaba! Ürün arayabilir, marka seçebilir veya sepeti yönetebilirsiniz.
        </p>
      </div>`;
    const inp = elInput(); if (inp) inp.focus();
    scrollToBottom();
  }

  // ------------------- USER MESSAGE -------------------
  function appendUser(text){
    const box = elMsgs(); if (!box) return;
    box.insertAdjacentHTML('beforeend',
      `<div class="chat-message chat-message-user"><p class="text-sm text-white leading-relaxed">${escapeHTML(text)}</p></div>`);
    scrollToBottom();
  }

  // ------------------- SEND / SEARCH -------------------
  function handleKey(e){
    if (e.key === 'Enter' && !e.shiftKey){ e.preventDefault(); send(); }
  }

  function send(){
    const inp = elInput(); if (!inp) return console.warn('[chat] input yok');
    const q = inp.value.trim(); if (!q) return;
    appendUser(q);
    inp.value = '';

    const products = (window.State?.products || []);
    const ql = q.toLowerCase();
    const results = products.filter(p =>
      [p.name, p.sku, p.brand, p.desc, p.description]
        .filter(Boolean)
        .some(v => String(v).toLowerCase().includes(ql))
    );

    renderProducts(results, { query: q, paginated: true });
  }

  // ------------------- RENDER: 5'li + Tümünü gör -------------------
  function renderProducts(list, ctx = {}){
    const box = elMsgs(); if (!box) return;
    const total = list.length;
    const slice = ctx.showAll ? list : list.slice(0, 5);
    const cards = slice.map(p => (window.Brands?.__card ? window.Brands.__card(p) : '')).join('') ||
                  `<p class="text-sm text-gray-400">Sonuç bulunamadı.</p>`;
    const head  = ctx.brand ? `<h4 class="text-sm font-semibold text-gray-200 mb-3 flex items-center gap-2">
                                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 24 24">
                                    <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
                                  </svg>
                                  ${ctx.brand} 
                                  <span class="text-xs text-gray-400 font-normal">(${total} ürün)</span>
                                </h4>` : '';

    box.insertAdjacentHTML('beforeend', `
      <div class="chat-message chat-message-bot">
        ${head}
        <div class="space-y-2.5">${cards}</div>
        ${(!ctx.showAll && total > 5)
          ? `<button class="mt-4 w-full text-sm text-white font-semibold py-3 px-4 rounded-xl bg-gradient-to-r from-orange-600/20 to-orange-700/20 border border-orange-500/30 hover:from-orange-600/30 hover:to-orange-700/30 hover:border-orange-500/50 transition-all hover:shadow-lg hover:shadow-orange-500/20 active:scale-95 flex items-center justify-center gap-2"
                     data-chat-more='${btoa(JSON.stringify(ctx))}'>
               <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" viewBox="0 0 24 24">
                 <path d="M16.59 8.59L12 13.17 7.41 8.59 6 10l6 6 6-6z"/>
               </svg>
               <span class="text-orange-400">${total - 5}</span> ürün daha — Tümünü gör
             </button>`
          : ``}
      </div>`
    );
    scrollToBottom();
  }

  // “Tümünü gör” delegasyonu
  document.addEventListener('click', (e)=>{
    const btn = e.target.closest('[data-chat-more]'); if (!btn) return;
    const ctx = JSON.parse(atob(btn.getAttribute('data-chat-more')));
    let list = [];

    if (ctx.brand) {
      list = (window.State?.products || []).filter(p => p.brand === ctx.brand);
    } else if (ctx.query) {
      const ql = ctx.query.toLowerCase();
      list = (window.State?.products || []).filter(p =>
        [p.name, p.sku, p.brand, p.desc, p.description]
          .filter(Boolean)
          .some(v => String(v).toLowerCase().includes(ql))
      );
    }

    renderProducts(list, { ...ctx, showAll: true });
    btn.remove();
  });

  // ------------------- İNCELE (detay modalı) -------------------
  function inspect(id){
    const p = (window.State?.products || []).find(x => String(x.id) === String(id));
    if (!p) return;
    
    // Doğrudan quantity modal'ı aç (yeni tasarım)
    if (window.Cart?.showAddProductModal) {
      window.Cart.showAddProductModal(p);
    }
  }

  // ------------------- VARYANT SEÇİCİ (productModal kullanır) -------------------
  function normalizeSku(s){ return String(s || '').replace(/\s+/g,'').toUpperCase(); }
  function explodeSkuTokens(skuField){
    // "WH 8146 / BK 8147, ZD330401" -> ["WH8146","BK8147","ZD330401"]
    const raw = String(skuField || '');
    const tokens = raw.match(/[A-Z0-9]+/gi) || [];
    return tokens.map(normalizeSku);
  }
  function findProductsBySkus(skuList){
    const wanted = skuList.map(normalizeSku);
    console.log('[findProductsBySkus] Aranan SKU\'lar (normalized):', wanted);
    
    const out = [];
    (window.State?.products || []).forEach(p=>{
      const tokens = explodeSkuTokens(p.sku);
      const normalized = normalizeSku(p.sku);
      
      // Hem tokenize hem de direkt SKU eşleşmesi kontrol et
      if (wanted.some(w => tokens.includes(w) || normalized === w || normalized.includes(w))) {
        out.push(p);
      }
    });
    
    console.log('[findProductsBySkus] Bulunan ürünler:', out.length);
    const seen = new Set();
    return out.filter(p => (seen.has(p.id) ? false : seen.add(p.id)));
  }

  // Eski productModal fonksiyonları kaldırıldı - artık Cart.showAddProductModal kullanılıyor

  async function openVariantPicker(skuList){
    console.log('[Chat.openVariantPicker] skuList:', skuList);
    
    const skuArray = String(skuList).split(/[,\/]+/).map(s=>s.trim()).filter(Boolean);
    console.log('[Chat.openVariantPicker] skuArray:', skuArray);
    
    const matches = findProductsBySkus(skuArray);
    console.log('[Chat.openVariantPicker] matches:', matches);

    // Tek eşleşme - doğrudan quantity modal aç
    if (matches.length === 1) {
      console.log('[Chat.openVariantPicker] Tek ürün bulundu, quantity modal açılıyor');
      if (window.Cart?.showAddProductModal) {
        window.Cart.showAddProductModal(matches[0]);
      }
      return;
    }

    // Çoklu eşleşme (varyantlar) - dinamik varyant seçici modal oluştur
    if (matches.length > 1) {
      console.log('[Chat.openVariantPicker] Çoklu ürün bulundu, varyant seçici açılıyor');
      const groupId = "variant-picker-" + Math.random().toString(36).slice(2);
      
      const html = `
        <div class="fixed inset-0 bg-black/60 z-50 flex items-center justify-center" id="${groupId}">
          <div class="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-6 w-full max-w-lg mx-4 border border-gray-600/50 shadow-2xl shadow-black/40">
            <div class="flex items-center justify-between mb-5">
              <h3 class="text-lg font-bold text-white">Varyasyon Seçiniz</h3>
              <button onclick="document.getElementById('${groupId}').remove()" class="text-gray-400 hover:text-white text-2xl leading-none transition-colors">✕</button>
            </div>
            <div class="space-y-2.5 max-h-96 overflow-y-auto chat-scroll">
              ${matches.map((p,i)=>{
                const price = p.price_display ? `<span class="text-orange-400 font-semibold ml-2">${escapeHTML(p.price_display)}</span>` : "";
                return `
                  <label class="flex items-center gap-3 bg-gradient-to-br from-gray-700/40 to-gray-800/60 border border-gray-600/50 hover:border-orange-500/40 rounded-xl p-3.5 cursor-pointer transition-all hover:shadow-lg hover:shadow-orange-500/10">
                    <input type="radio" name="${groupId}-radio" data-product-id="${escapeHTML(String(p.id))}" ${i===0?'checked':''} class="w-4 h-4 text-orange-600 bg-gray-700 border-gray-600 focus:ring-orange-500 focus:ring-2" />
                    <div class="flex-1 min-w-0">
                      <div class="text-sm font-semibold text-white mb-1.5 leading-relaxed">${escapeHTML(p.name || '-')}</div>
                      <div class="text-xs text-gray-400"><span class="text-orange-400 font-medium">${escapeHTML(p.brand || '')}</span> • <span class="font-mono">${escapeHTML(p.sku || '')}</span>${price}</div>
                    </div>
                  </label>`;
              }).join('')}
            </div>
            <button id="${groupId}-btn" class="mt-5 w-full bg-gradient-to-r from-orange-600 to-orange-700 hover:from-orange-500 hover:to-orange-600 text-white font-semibold py-3 px-4 rounded-xl transition-all hover:shadow-lg hover:shadow-orange-500/30 active:scale-95">
              Devam Et
            </button>
          </div>
        </div>`;
      
      document.body.insertAdjacentHTML('beforeend', html);
      
      // Event listener ekle
      document.getElementById(`${groupId}-btn`).addEventListener('click', () => {
        const sel = document.querySelector(`input[name="${groupId}-radio"]:checked`);
        if (sel && window.Cart?.showAddProductModal) {
          const productId = sel.getAttribute('data-product-id');
          const product = (window.State?.products || []).find(p => String(p.id) === String(productId));
          if (!product) {
            console.warn('[Chat.openVariantPicker] Seçilen ürün bulunamadı. id:', productId);
            Toast.show('Seçilen varyant bulunamadı.', 'warn');
            return;
          }
          window.Cart.showAddProductModal(product);
        }
        document.getElementById(groupId).remove();
      });
      
      return;
    }

    
    // Hiç eşleşme yok
    console.warn('[Chat.openVariantPicker] Hiç ürün bulunamadı! SKU array:', skuArray);
    Toast.show('Bu SKU(lar) için ürün bulunamadı.', 'warn');
  }

  
  // ------------------- PUBLIC API -------------------
  return {
    send, handleKey, renderProducts, inspect, clear,
    openVariantPicker,
    showProductModal: openVariantPicker  // Alias for external calls (iframe)
  };
})();
