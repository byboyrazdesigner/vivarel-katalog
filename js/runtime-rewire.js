/* /js/runtime-rewire.js */
(function(){
  // SKU normalizasyonu: token içi boşlukları sil, en/em dash → '-'
  function normalizeSkuList(s){
    if (!s) return "";
    return String(s)
      .replace(/[–—]/g, "-")     // en/em dash -> normal tire
      .split(",")
      .map(t => t.trim().replace(/\s+/g, "")) // "BK 3456" -> "BK3456"
      .filter(Boolean)
      .join(",");
  }

  function extractSkuFromHref(href){
    // javascript:window.parent.postMessage({type:'add-to-cart',sku:'WH2360,BK 2361'},'*')
    const m = String(href).match(/sku\s*:\s*['"]([^'"]+)['"]/i);
    return m ? normalizeSkuList(m[1]) : null;
  }

  function rewireAnchor(a){
    if (!a || a.__rewired) return;
    const href = a.getAttribute("href") || "";
    if (!href.startsWith("javascript:")) return;

    const skuFromHref = extractSkuFromHref(href);
    if (!skuFromHref) return;

    a.setAttribute("href", "#");
    a.setAttribute("data-sku", skuFromHref);

    // class ekle (varsa eklemeyelim)
    const cls = a.getAttribute("class") || "";
    if (!/\bbtn-cart\b/.test(cls)) a.setAttribute("class", (cls + " btn-cart").trim());

    // güvenli click handler: doğrudan Chat köprüsüne gönder
    a.addEventListener("click", function(ev){
      ev.preventDefault();
      try {
        // Tercih: aynı origin postMessage; değilse doğrudan Chat.openVariantPicker
        const payload = { type: "add-to-cart", sku: skuFromHref };
        if (window.parent && window.parent !== window && location.origin === document.location.origin) {
          window.parent.postMessage(payload, location.origin);
        } else if (window.Chat?.openVariantPicker) {
          window.Chat.openVariantPicker(skuFromHref);
        }
      } catch (_) {
        window.Chat?.openVariantPicker && window.Chat.openVariantPicker(skuFromHref);
      }
    }, { passive:false });

    a.__rewired = true;
  }

  function scan(root){
    root.querySelectorAll('a[href^="javascript:"]').forEach(rewireAnchor);
  }

  // İlk yükleme
  document.addEventListener("DOMContentLoaded", function(){
    scan(document);

    // iOS / dinamik in5 DOM’u için izleme
    const mo = new MutationObserver(muts=>{
      for (const m of muts){
        m.addedNodes && m.addedNodes.forEach(n=>{
          if (n.nodeType === 1) {
            if (n.matches?.('a[href^="javascript:"]')) rewireAnchor(n);
            n.querySelectorAll?.('a[href^="javascript:"]').forEach(rewireAnchor);
          }
        });
      }
    });
    mo.observe(document.documentElement, {childList:true, subtree:true});
  });
})();
