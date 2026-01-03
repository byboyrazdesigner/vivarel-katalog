// /assistant/loader.js — injects the Assistant UI on brand pages without iframes
(function(){
  function inferBrand(){
    try{
      const scripts = document.getElementsByTagName("script");
      for (let i=scripts.length-1;i>=0;i--){
        const s = scripts[i];
        if ((s.src||"").includes("/assistant/loader.js")) {
          const b = s.getAttribute("data-brand");
          if (b) return b;
        }
      }
    }catch(_){}
    const m = location.pathname.match(/\/Markalar\/([^\/]+)\//i);
    if (m) {
      const folder = decodeURIComponent(m[1]);
      const back = { "ZoneDenmark":"ZoneDenmark","GEFU":"GEFU","Umbra":"Umbra","Yamazaki":"Yamazaki",
                     "Bitz":"Bitz","Rosti":"Rosti","VillaCollection":"VillaCollection","LyngbyGlass":"LyngbyGlass",
                     "ARIT":"ARIT","BAOLGI":"BAOLGI","Hailo":"Hailo","Foppapedretti":"Foppapedretti",
                     "GENSE":"Gense","LeFeu":"Le Feu","TEM":"tem" };
      return back[folder] || folder;
    }
    return (window.Config && window.Config.DEFAULT_BRAND) || "ZoneDenmark";
  }

  const style = document.createElement("style");
  style.textContent = `
    html.assistant-lock, body.assistant-lock { overflow: hidden !important; }
    #ai-assistant-fab{
      position:fixed; right:16px; bottom:16px; z-index: 2147483646;
      width:56px; height:56px; border-radius:9999px; display:flex; align-items:center; justify-content:center;
      background:#0f172a; color:#fff; box-shadow:0 8px 24px rgba(0,0,0,.35); border:none; cursor:pointer;
    }
    #ai-assistant-fab:hover{ background:#1e293b; }
    #ai-assistant-overlay{
      position:fixed; inset:0; background:rgba(0,0,0,.45); z-index:2147483645; display:none;
    }
    #ai-assistant-overlay.open{ display:block; }
    #ai-assistant-panel{
      position:fixed; right:24px; bottom:24px; top:24px;
      width: min(420px, 92vw);
      max-height: calc(100vh - 48px);
      z-index:2147483647;
      background:#111827; color:#e5e7eb;
      border:1px solid #374151; border-radius:16px;
      display:none; flex-direction:column; overflow:hidden;
      box-shadow: 0 12px 40px rgba(0,0,0,.45);
    }
    #ai-assistant-panel.open{ display:flex; }
    #ai-assistant-panel header{ padding:12px 14px; border-bottom:1px solid #374151; display:flex; align-items:center; justify-content:space-between; }
    #ai-assistant-panel .chips{ padding:12px 14px; border-bottom:1px solid #374151; display:flex; flex-wrap:wrap; gap:8px; }
    #ai-assistant-panel .chip{ background:#1f2937; color:#e5e7eb; border:1px solid #4b5563; border-radius:9999px; padding:6px 10px; font-size:12px; cursor:pointer; }
    #ai-assistant-panel .chip:hover{ background:#374151; }
    #ai-assistant-panel .body{ flex:1; overflow:auto; padding:12px 14px; }
    #ai-assistant-panel .card{ background:#1f2937; border:1px solid #4b5563; border-radius:10px; padding:10px; margin-bottom:10px; }
    #ai-assistant-panel .row{ display:flex; gap:8px; }
    #ai-assistant-panel .btn{ border:none; border-radius:8px; padding:8px 10px; font-size:12px; cursor:pointer; }
    #ai-assistant-panel .btn-primary{ background:#ea580c; color:#fff; }
    #ai-assistant-panel .btn-muted{ background:#4b5563; color:#fff; }
    @media (max-width: 640px){
      #ai-assistant-panel{ right:12px; left:12px; bottom:12px; top:12px; width:auto; }
    }
  `;
  document.head.appendChild(style);

  const overlay = document.createElement("div");
  overlay.id = "ai-assistant-overlay";
  const panel = document.createElement("div");
  panel.id = "ai-assistant-panel";
  panel.innerHTML = `
    <header>
      <div style="font-weight:600">Tem 2025</div>
      <div class="row">
        <button id="aa-clear" class="btn btn-muted">Sohbeti Temizle</button>
        <button id="aa-cart" class="btn btn-muted">Sepetim <span id="aa-badge" style="display:none;margin-left:6px;background:#ea580c;color:#fff;border-radius:9999px;padding:0 6px;font-size:11px;"></span></button>
        <button id="aa-close" class="btn btn-muted">✕</button>
      </div>
    </header>
    <div class="chips" id="aa-chips"></div>
    <div class="body">
      <div id="aa-messages">
        <div class="card">Merhaba! Ürün arayabilir, marka seçebilir veya sepeti yönetebilirsiniz.</div>
      </div>
    </div>
    <div style="border-top:1px solid #374151; padding:10px 12px; display:flex; gap:8px;">
      <input id="aa-input" placeholder="Ürün ara veya soru sor..." style="flex:1; background:#1f2937; color:#e5e7eb; border:1px solid #4b5563; border-radius:10px; padding:8px 10px; font-size:14px;" />
      <button id="aa-send" class="btn btn-primary">Gönder</button>
    </div>
  `;
  const fab = document.createElement("button");
  fab.id = "ai-assistant-fab";
  fab.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="currentColor" viewBox="0 0 24 24"><path d="M20 2H4a2 2 0 0 0-2 2v14l4-4h14a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2z"/></svg>`;

  document.body.appendChild(overlay);
  document.body.appendChild(panel);
  document.body.appendChild(fab);

  document.getElementById("aa-close").addEventListener("click", ()=>{
    if (window.Mobile && window.Mobile.closeChat) window.Mobile.closeChat();
    else { panel.classList.remove("open"); overlay.classList.remove("open"); }
  });

  function renderChips(brands, activeBrand){
    const box = document.getElementById("aa-chips");
    box.innerHTML = "";
    brands.forEach(b=>{
      const el = document.createElement("button");
      el.className = "chip";
      el.textContent = b;
      if (b === activeBrand) el.style.outline = "2px solid #ea580c";
      el.addEventListener("click", ()=>{
        if (window.Config && window.Config.brandToSrc) {
          const href = window.Config.brandToSrc(b);
          if (href && location.pathname !== href) location.href = href;
        }
      });
      box.appendChild(el);
    });
  }

  function loadScript(src){
    return new Promise((resolve,reject)=>{
      const s = document.createElement("script");
      s.src = src;
      s.onload = resolve; s.onerror = reject;
      document.head.appendChild(s);
    });
  }

  (async function boot(){
      // İframe içindeyse loader'ı çalıştırma (sonsuz döngü önlemi)
    if (window.self !== window.top) {
      console.log('[loader] Running inside iframe, skipping boot to prevent loop');
      return;
    }
    try{
      await loadScript("/js/config.js?v=13");
      await loadScript("/js/mobile.js?v=3");
      await loadScript("/js/state.js?v=12");
      await loadScript("/js/data.js?v=12");
      await loadScript("/js/cart.js?v=12");
      await loadScript("/js/chat.js?v=12");
      await loadScript("/js/brands.js?v=12");

      const brand = inferBrand();
      const allBrands = (window.Config.BRAND_ORDER && window.Config.BRAND_ORDER.length)
        ? window.Config.BRAND_ORDER
        : Array.from(new Set((window.State?.products||[]).map(p=>p.brand)));
      renderChips(allBrands, brand);

      if (window.Brands && window.Brands.select) window.Brands.select(brand);

      setInterval(()=>{
        const badge = document.getElementById("aa-badge");
        try{
          const n = (window.Cart && window.Cart.items && window.Cart.items.length) || 0;
          if (!badge) return;
          if (n > 0) { badge.style.display="inline-block"; badge.textContent = String(n); }
          else { badge.style.display="none"; }
        }catch(_){}
      }, 800);
    }catch(e){
      console.error("Assistant loader boot error:", e);
    }
// noop loader: sayfayı kırmadan data-brand'ı görmezden gelir
(function () {
  window.AssistantLoader = {
    init: function(){}, mount: function(){}, version: "noop-1"
  };
})();

})();
