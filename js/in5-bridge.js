/* in5-bridge.js — iOS/kurumsal uyumlu, idempotent köprü
   İşlev: in5 export içindeki "javascript:window.parent.postMessage(...)" ve [data-sku] linklerini güvenli click handler ile yeniden bağlar. */

(function(){
  var BOUND_FLAG = "__in5BridgeBound";

  function normalizeSku(s){
    return String(s||"").trim();
  }

  function extractSkuFromHref(href){
    // ör: javascript:window.parent.postMessage({type:'add-to-cart',sku:'WH2360,BK2361'},'*')
    var m = String(href||"").match(/sku\s*:\s*'([^']+)'/i);
    return m ? normalizeSku(m[1]) : null;
  }

  function postToParent(sku){
    var payload = { type: "add-to-cart", sku: sku };
    try {
      // Aynı origin hedefi — kurumsal tarayıcı/iOS için şart
      var tgt = location.origin;
      if (window.parent && window.parent !== window) {
        window.parent.postMessage(payload, tgt);
      }
    } catch (e) {
      // parent erişilemezse sessiz geç
      console.warn("[in5-bridge] parent.postMessage hata:", e);
    }
  }

  function bind(el, getSku){
    if (!el || el[BOUND_FLAG]) return;
    el[BOUND_FLAG] = true;
    el.addEventListener("click", function(ev){
      // bazı in5 temalarında SVG/IMG içindeki tıklamalar için en yakın link
      var a = ev.target.closest("a,[data-sku]");
      var sku = getSku(a);
      if (!sku) return;
      ev.preventDefault();
      ev.stopPropagation();
      postToParent(sku);
    }, {passive:false});
  }

  function sweep(root){
    root = root || document;

    // 1) javascript:window.parent.postMessage(...) kullanan tüm <a>’lar
    var jsLinks = root.querySelectorAll('a[href^="javascript:"]');
    jsLinks.forEach(function(a){
      var sku = extractSkuFromHref(a.getAttribute("href"));
      if (!sku) return;
      // güvenli dummy href
      a.setAttribute("href", "#");
      // SKU’yu ayrıca data-sku’ya da yazarız (ileride işimize yarar)
      a.setAttribute("data-sku", sku);
      bind(a, function(node){ return extractSkuFromHref(node.getAttribute("href")) || node.getAttribute("data-sku"); });
    });

    // 2) Zaten data-sku kullanan buton/anchor’lar
    var dataLinks = root.querySelectorAll("[data-sku]");
    dataLinks.forEach(function(a){
      bind(a, function(node){ return normalizeSku(node.getAttribute("data-sku")); });
    });
  }

  // İlk tarama
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function(){ sweep(document); });
  } else {
    sweep(document);
  }

  // in5 sayfaları dinamik öğe ekleyebilir — gözlemle
  try {
    var mo = new MutationObserver(function(muts){
      for (var i=0;i<muts.length;i++){
        var n = muts[i].target;
        sweep(n);
      }
    });
    mo.observe(document.documentElement, { childList:true, subtree:true });
  } catch(e){}
})();
