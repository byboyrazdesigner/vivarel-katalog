// /js/cart.js — FULL REPLACE (localStorage fallback + Toast + secure postMessage)
(function () {
  const LS_KEY = "tem_cart_v1";

  // ---------------- localStorage Fallback (kurumsal/iOS kısıtları) ----------------
  let MEM = [];
  let lsOK = true;
  try {
    localStorage.setItem("__t", "1");
    localStorage.removeItem("__t");
  } catch {
    lsOK = false;
  }
  function load() {
    try {
      return lsOK ? JSON.parse(localStorage.getItem(LS_KEY) || "[]") : MEM;
    } catch {
      return lsOK ? [] : MEM;
    }
  }
  function save(items) {
    if (lsOK) {
      localStorage.setItem(LS_KEY, JSON.stringify(items));
    } else {
      MEM = items;
    }
  }

  // ---------------- Toast Helper (uçan bildirim) ----------------
  const Toast = (function () {
    let stack = null;
    function ensure() {
      if (stack) return;
      stack = document.createElement("div");
      stack.id = "toastStack";
      stack.style.cssText =
        "position:fixed;right:16px;bottom:16px;z-index:9999;display:flex;flex-direction:column;gap:8px;pointer-events:none";
      document.body.appendChild(stack);
    }
    function show(msg, type = "info") {
      ensure();
      const bg = type === "success" 
        ? "linear-gradient(135deg, #065f46 0%, #047857 100%)" 
        : type === "warn" 
        ? "linear-gradient(135deg, #92400e 0%, #b45309 100%)" 
        : "linear-gradient(135deg, #374151 0%, #4b5563 100%)";
      const border = type === "success" ? "#10b981" : type === "warn" ? "#f59e0b" : "#9ca3af";
      const shadow = type === "success" 
        ? "0 10px 25px rgba(16, 185, 129, 0.3)" 
        : type === "warn" 
        ? "0 10px 25px rgba(245, 158, 11, 0.3)" 
        : "0 10px 25px rgba(0, 0, 0, 0.25)";
      const el = document.createElement("div");
      el.style.cssText = `
        min-width:260px;max-width:90vw;color:#fff;background:${bg};
        border:1px solid ${border};border-radius:12px;padding:12px 16px;
        box-shadow:${shadow};opacity:0;transform:translateY(12px) scale(0.95);
        transition:all .3s cubic-bezier(0.4, 0, 0.2, 1);pointer-events:auto;
        font-size:13px;line-height:1.4;font-weight:500;backdrop-filter:blur(10px);
      `;
      el.textContent = msg;
      stack.appendChild(el);
      requestAnimationFrame(() => {
        el.style.opacity = "1";
        el.style.transform = "translateY(0) scale(1)";
      });
      setTimeout(() => {
        el.style.opacity = "0";
        el.style.transform = "translateY(-8px) scale(0.95)";
        setTimeout(() => el.remove(), 300);
      }, 2400);
    }
    return { show };
  })();

  // ---------------- Helpers ----------------
  function getProducts() {
    return window.State && Array.isArray(window.State.products) ? window.State.products : [];
  }
  function findProduct(id) {
    return getProducts().find((p) => String(p.id) === String(id));
  }
  function priceValue(p) {
    if (typeof p?.price_value === "number") return p.price_value;
    if (typeof p?.price === "number") return p.price;
    if (typeof p?.price_display === "string") {
      const n = p.price_display.replace(/[^\d,.-]/g, "").replace(/\./g, "").replace(",", ".");
      const v = parseFloat(n);
      return isNaN(v) ? 0 : v;
    }
    return 0;
  }
  const fmtTRY = (n) =>
    window.Price?.formatTRY
      ? window.Price.formatTRY(n)
      : new Intl.NumberFormat("tr-TR", { style: "currency", currency: "TRY", maximumFractionDigits: 2 }).format(n);
  const fmtNumTR = (n) =>
    new Intl.NumberFormat("tr-TR", { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(+n || 0);
  function total(items) {
    return items.reduce((sum, it) => {
      // SKU veya ID ile ürünü bul
      const p = it.sku 
        ? getProducts().find(x => String(x.sku) === String(it.sku))
        : findProduct(it.id);
      return sum + priceValue(p) * (it.qty || 1);
    }, 0);
  }

  // ---------------- Cart API ----------------
  const Cart = {
    quickAdd(id) {
      const items = load();
      const idx = items.findIndex((x) => String(x.id) === String(id));
      if (idx >= 0) items[idx].qty = (items[idx].qty || 1) + 1;
      else items.push({ id, qty: 1 });
      save(items);
      Cart.updateBadge();
      Toast.show("Ürün sepete eklendi.", "success");
    },

    remove(key) {
      save(load().filter((x) => String(x.sku || x.id) !== String(key)));
      Cart.renderModal();
      Cart.updateBadge();
    },

    clear() {
      save([]);
      Cart.renderModal();
      Cart.updateBadge();
    },

    updateBadge() {
      const badge = document.getElementById("cartBadge");
      if (!badge) return;
      const count = load().reduce((s, x) => s + (x.qty || 1), 0);
      if (count > 0) {
        badge.textContent = count;
        badge.classList.remove("hidden");
        badge.classList.add("flex");
      } else {
        badge.classList.add("hidden");
        badge.classList.remove("flex");
      }
    },

    showModal() {
      const m = document.getElementById("cartModal");
      if (!m) return;
      Cart.renderModal();
      m.classList.remove("hidden");
      m.classList.add("flex");
    },
    hideModal() {
      const m = document.getElementById("cartModal");
      if (!m) return;
      m.classList.add("hidden");
      m.classList.remove("flex");
    },

    renderModal() {
      const box = document.getElementById("cartModalItems");
      const totalEl = document.getElementById("cartTotal");
      if (!box || !totalEl) return;

      const items = load();
      if (items.length === 0) {
        box.innerHTML = `
          <div class="text-center py-12">
            <div class="w-20 h-20 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-gray-700/40 to-gray-800/60 border border-gray-600/50 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" fill="currentColor" viewBox="0 0 24 24" class="text-gray-500">
                <path d="M7 18c-1.1 0-1.99.9-1.99 2S5.9 22 7 22s2-.9 2-2-.9-2-2-2zM1 2v2h2l3.6 7.59-1.35 2.45c-.16.28-.25.61-.25.96 0 1.1.9 2 2 2h12v-2H7.42c-.14 0-.25-.11-.25-.25l.03-.12.9-1.63h7.45c.75 0 1.41-.41 1.75-1.03l3.58-6.49c.08-.14.12-.31.12-.48 0-.55-.45-1-1-1H5.21l-.94-2H1zm16 16c-1.1 0-1.99.9-1.99 2s.89 2 1.99 2 2-.9 2-2-.9-2-2-2z"/>
              </svg>
            </div>
            <p class="text-gray-400 text-sm font-medium">Sepetiniz boş</p>
            <p class="text-gray-500 text-xs mt-1">Ürün eklemek için katalogları inceleyin</p>
          </div>`;
        totalEl.textContent = fmtTRY(0);
        return;
      }

      box.innerHTML = items
        .map((it) => {
          // SKU veya ID ile ürünü bul
          const itemKey = it.sku || it.id;
          const p = it.sku 
            ? getProducts().find(x => String(x.sku) === String(it.sku)) 
            : findProduct(it.id);
          if (!p) return "";
          const q = it.qty || 1;
          const line = priceValue(p) * q;
          const priceTxt = p.price_display || fmtTRY(priceValue(p));
          const productImage = Cart._getProductImage(p);
          
          return `
          <div class="bg-gradient-to-br from-gray-700/40 to-gray-800/60 border border-gray-600/50 rounded-xl p-4 hover:border-orange-500/30 hover:shadow-lg hover:shadow-orange-500/10 transition-all duration-200">
            <div class="flex items-start gap-3 mb-4">
              ${productImage ? `
              <div class="flex-shrink-0 w-20 h-20 bg-white rounded-lg overflow-hidden border border-gray-600">
                <img src="${productImage}" 
                     alt="${p.name}" 
                     class="w-full h-full object-contain p-1"
                     onerror="this.parentElement.style.display='none'" />
              </div>
              ` : ''}
              <div class="flex-1 min-w-0">
                <div class="text-sm font-semibold text-white mb-1.5 line-clamp-2 leading-relaxed">${p.name}</div>
                <div class="flex items-center gap-2 text-xs">
                  <span class="text-orange-400 font-medium">${p.brand}</span>
                  <span class="text-gray-500">•</span>
                  <span class="text-gray-400 font-mono">${p.sku}</span>
                </div>
              </div>
              <div class="text-right flex-shrink-0">
                <div class="text-sm font-bold text-orange-400 mb-0.5">${priceTxt}</div>
                <div class="text-xs text-gray-400 font-semibold bg-gray-800/50 px-2 py-0.5 rounded">${fmtTRY(line)}</div>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <div class="flex items-center bg-gray-800/80 rounded-lg border border-gray-600/60 shadow-inner">
                <button class="px-3 py-2 text-gray-300 hover:text-orange-400 hover:bg-gray-700/60 rounded-l-lg transition-all active:scale-95" 
                        onclick="Cart.dec('${itemKey}')" title="Azalt">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M19 13H5v-2h14v2z"/>
                  </svg>
                </button>
                <span class="px-5 py-2 text-sm font-bold text-white border-x border-gray-600/60 min-w-[3.5rem] text-center bg-gray-900/40">${q}</span>
                <button class="px-3 py-2 text-gray-300 hover:text-orange-400 hover:bg-gray-700/60 rounded-r-lg transition-all active:scale-95" 
                        onclick="Cart.inc('${itemKey}')" title="Artır">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
                  </svg>
                </button>
              </div>
              <button class="ml-auto px-3.5 py-2 text-xs bg-rose-600/90 hover:bg-rose-600 text-white rounded-lg transition-all hover:shadow-lg hover:shadow-rose-500/30 active:scale-95 flex items-center gap-1.5 font-medium" 
                      onclick="Cart.remove('${itemKey}')" title="Sepetten Kaldır">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                </svg>
                Kaldır
              </button>
            </div>
          </div>`;
        })
        .join("");

      totalEl.textContent = fmtTRY(total(items));
    },

    inc(key) {
      const items = load();
      const it = items.find((x) => String(x.sku || x.id) === String(key));
      if (it) it.qty = (it.qty || 1) + 1;
      save(items);
      Cart.renderModal();
      Cart.updateBadge();
    },
    dec(key) {
      const items = load();
      const it = items.find((x) => String(x.sku || x.id) === String(key));
      if (it) it.qty = Math.max(1, (it.qty || 1) - 1);
      save(items);
      Cart.renderModal();
      Cart.updateBadge();
    },

    // ---------- CSV export (TR biçemi; ; ayraç) ----------
    exportCSV() {
      const items = load();
      if (items.length === 0) return;

      const rows = [["OrderCode", "Brand", "Name", "SKU", "Qty", "Price", "LineTotal", "Page"]];
      const oc = Cart._orderCode();

      items.forEach((it) => {
        const p = findProduct(it.id);
        if (!p) return;
        const q = it.qty || 1;
        const price = priceValue(p);
        const line = price * q;
        rows.push([oc, p.brand || "", p.name || "", p.sku || "", q, fmtNumTR(price), fmtNumTR(line), p.page ?? ""]);
      });

      const csv = rows.map((r) => r.map((x) => `"${String(x).replace(/"/g, '""')}"`).join(";")).join("\n");

      const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = `sepet_${oc}.csv`;
      a.click();
      URL.revokeObjectURL(a.href);
    },

    // ---------- E-posta gönder ----------
    async sendEmail() {
      const items = load();
      if (items.length === 0) {
        alert("Sepet boş.");
        return;
      }

      // Yeni form alanlarını al
      const name = (document.getElementById("senderName") || {}).value?.trim();
      const company = (document.getElementById("senderCompany") || {}).value?.trim();
      const phone = (document.getElementById("senderPhone") || {}).value?.trim();
      const email = (document.getElementById("senderEmail") || {}).value?.trim();
      
      // Validasyon
      if (!name) {
        alert("Ad Soyad alanı zorunludur.");
        return;
      }
      if (!company) {
        alert("Firma ismi zorunludur.");
        return;
      }
      if (!phone) {
        alert("Telefon alanı zorunludur.");
        return;
      }
      
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!email || !emailRegex.test(email)) {
        alert("Geçerli bir e-posta adresi giriniz.");
        return;
      }

      const oc = Cart._orderCode();
      const mailEnv = Cart._mailEnv();
      const mailEndpoint = Cart._mailEndpoint(mailEnv);
      const payload = {
        order_code: oc,
        sender_name: name,
        sender_company: company,
        sender_phone: phone,
        sender_email: email,
        total_value: total(items),
        currency: "TRY",
        mail_env: mailEnv,
        items: items.map((it) => {
          const p = findProduct(it.id) || {};
          return {
            id: p.id,
            brand: p.brand,
            name: p.name,
            sku: p.sku,
            page: p.page ?? null,
            qty: it.qty || 1,
            price_value: priceValue(p),
            price_display: p.price_display || null,
            image: Cart._getProductImage(p) || null,
          };
        }),
      };

      // Debug: payload'ı konsola yazdır
      console.log('[Cart.sendEmail] Payload:', payload);

      try {
        const res = await fetch(mailEndpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        
        console.log('[Cart.sendEmail] Response status:', res.status);
        
        if (!res.ok) {
          const errorText = await res.text();
          console.error('[Cart.sendEmail] Error response:', errorText);
          throw new Error(`HTTP ${res.status}: ${errorText}`);
        }
        
        const data = await res.json();
        console.log('[Cart.sendEmail] Response data:', data);
        alert(data?.message || "Sepet e-posta ile gönderildi.");
      } catch (e) {
        console.error('[Cart.sendEmail] Exception:', e);
        alert("E-posta gönderilemedi: " + e.message);
      }
    },

    _orderCode() {
      const d = new Date();
      const ymd = `${d.getFullYear()}${String(d.getMonth() + 1).padStart(2, "0")}${String(d.getDate()).padStart(2, "0")}`;
      const rnd = Math.random().toString(36).slice(2, 6).toUpperCase();
      return `KTLG-${ymd}-${rnd}`;
    },

    _mailEnv() {
      const forced = (window.TEM_MAIL_ENV ?? window.CartMailEnv ?? "").toString().trim().toLowerCase();
      if (forced === "prod" || forced === "test") return forced;

      const host = (window.location?.hostname || "").toLowerCase();
      if (!host) return "prod";
      if (host === "localhost" || host === "127.0.0.1" || host.endsWith(".local")) return "test";
      if (host.endsWith(".test") || host.includes("staging")) return "test";
      return "prod";
    },

    _mailEndpoint(env) {
      const forcedEndpoint = (window.TEM_MAIL_ENDPOINT ?? window.CartMailApiBase ?? "").toString().trim();
      if (forcedEndpoint) return forcedEndpoint;

      const currentEnv = env || Cart._mailEnv();
      if (currentEnv !== "test") return "/api/phpmailer_send.php";

      const loc = window.location || {};
      const protocol = loc.protocol || "http:";
      const hostname = (loc.hostname || "").toLowerCase();
      const port = String(loc.port || "").trim();

      const sameHost = hostname === "127.0.0.1" || hostname === "localhost";
      const samePort = port === "8000" || port === "";

      if (sameHost && samePort) {
        return "/api/phpmailer_send.php";
      }

      return `${protocol}//127.0.0.1:8000/api/phpmailer_send.php`;
    },

    // 📍 SAYFAYA GİT - iframe'deki katalogda SKU'yu bulup o sayfaya gider
    // ZONE ürünleri farklı kataloglarda olabilir, sırasıyla dener
    goToProductPage(sku) {
      if (!sku) {
        Toast.show("Ürün kodu eksik!", "warn");
        return;
      }

      const normalizedSku = String(sku).replace(/\s+/g, '').toUpperCase();
      
      // Ürünü products.json'dan bul
      const product = getProducts().find(p => {
        const pSku = String(p.sku || '').replace(/\s+/g, '').toUpperCase();
        return pSku === normalizedSku || pSku.includes(normalizedSku);
      });

      if (!product) {
        Toast.show("Ürün bulunamadı!", "warn");
        return;
      }

      // Aktif katalogdan markayı çıkar
      const iframe = document.getElementById('brandFrame');
      const currentSrc = iframe?.src || '';
      const brandMatch = currentSrc.match(/\/Markalar\/([^\/]+)\//);
      const currentBrand = brandMatch ? brandMatch[1] : null;

      // Ürünün markasını belirle
      let productBrand = product.brand;
      
      // ZONE markalı ürünler 3 farklı katalogda olabilir
      // Önce aktif katalogda ara, bulamazsa diğerlerini dene
      const zoneCatalogs = ['ZONE_DENMARK', 'ZONE_DENMARK_BANYO', 'ZONE_DENMARK_MUTFAK'];
      
      if (productBrand === 'ZONE') {
        // Aktif katalog ZONE kataloglarından biriyse, önce orada ara
        if (zoneCatalogs.includes(currentBrand)) {
          console.log('[goToProductPage] ZONE ürünü, aktif katalogda aranıyor:', currentBrand);
          const found = Cart._navigateToSkuInCatalog(normalizedSku);
          if (found) return;
          
          // Bulunamadı, diğer ZONE kataloglarını dene
          const otherCatalogs = zoneCatalogs.filter(c => c !== currentBrand);
          Cart._tryZoneCatalogs(normalizedSku, otherCatalogs, 0);
        } else {
          // Aktif katalog ZONE değil, sırasıyla ZONE kataloglarını dene
          Cart._tryZoneCatalogs(normalizedSku, zoneCatalogs, 0);
        }
        return;
      }

      console.log('[goToProductPage] Ürün markası:', productBrand, 'Aktif marka:', currentBrand);

      // ZONE dışı markalar için normal akış
      if (productBrand && currentBrand && productBrand !== currentBrand) {
        Toast.show(`${productBrand.replace(/_/g, ' ')} kataloğu yükleniyor...`, "info");
        
        const modal = document.getElementById('addProductModal');
        if (modal) modal.remove();
        
        if (window.Brands?.select) {
          window.Brands.select(productBrand);
          setTimeout(() => Cart._navigateToSkuInCatalog(normalizedSku), 2000);
        }
        return;
      }

      // Aynı marka - doğrudan sayfaya git
      Cart._navigateToSkuInCatalog(normalizedSku);
    },

    // ZONE kataloglarını sırasıyla dene
    _tryZoneCatalogs(normalizedSku, catalogs, index) {
      if (index >= catalogs.length) {
        Toast.show("Ürün ZONE kataloglarında bulunamadı", "warn");
        return;
      }

      const catalog = catalogs[index];
      console.log('[_tryZoneCatalogs] Deneniyor:', catalog);
      Toast.show(`${catalog.replace(/_/g, ' ')} katalogunda aranıyor...`, "info");

      const modal = document.getElementById('addProductModal');
      if (modal) modal.remove();

      if (window.Brands?.select) {
        window.Brands.select(catalog);
        
        setTimeout(() => {
          const found = Cart._navigateToSkuInCatalog(normalizedSku);
          if (!found) {
            // Bu katalogda bulunamadı, sonrakini dene
            Cart._tryZoneCatalogs(normalizedSku, catalogs, index + 1);
          }
        }, 2000);
      }
    },

    // İç fonksiyon: Aktif katalogda SKU'yu bul ve sayfaya git
    // Bulunduysa true, bulunamadıysa false döner
    _navigateToSkuInCatalog(normalizedSku) {
      const iframe = document.getElementById('brandFrame');
      if (!iframe || !iframe.contentDocument) {
        console.log('[_navigateToSkuInCatalog] Katalog yüklü değil');
        return false;
      }

      try {
        const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
        
        // SKU'yu içeren elementi bul (buton href'inde veya data-sku'da)
        const allLinks = iframeDoc.querySelectorAll('a[href*="sku"], [data-sku]');
        let targetPage = null;
        
        for (const link of allLinks) {
          const href = link.getAttribute('href') || '';
          const dataSku = link.getAttribute('data-sku') || '';
          const linkSku = (href.match(/sku:'([^']+)'/i) || [])[1] || dataSku;
          
          if (linkSku && linkSku.replace(/\s+/g, '').toUpperCase().includes(normalizedSku)) {
            // Bu linkin hangi sayfada olduğunu bul
            const page = link.closest('.page, [data-name]');
            if (page) {
              targetPage = page.getAttribute('data-name');
              break;
            }
          }
        }

        if (targetPage) {
          // in5 slider'ı bu sayfaya götür
          const slider = iframe.contentWindow.jQuery?.('#slider');
          if (slider && slider.anythingSlider) {
            const pageIndex = Array.from(iframeDoc.querySelectorAll('.page[data-name]'))
              .findIndex(p => p.getAttribute('data-name') === targetPage);
            if (pageIndex >= 0) {
              slider.anythingSlider(pageIndex + 1); // 1-indexed
              Toast.show(`Sayfa ${targetPage}'e gidildi`, "success");
              
              // Modal'ı kapat
              const modal = document.getElementById('addProductModal');
              if (modal) modal.remove();
              return true;
            }
          }
          
          // Fallback: scrollIntoView
          const targetEl = iframeDoc.querySelector(`.page[data-name="${targetPage}"]`);
          if (targetEl) {
            targetEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
            Toast.show(`Sayfa ${targetPage}'e gidildi`, "success");
            
            // Modal'ı kapat
            const modal = document.getElementById('addProductModal');
            if (modal) modal.remove();
            return true;
          }
        }

        console.log('[_navigateToSkuInCatalog] SKU bu katalogda bulunamadı:', normalizedSku);
        return false;
      } catch (e) {
        console.error('[_navigateToSkuInCatalog] Hata:', e);
        return false;
      }
    },

    // 🛒 IN5'TEN GELEN SKU İÇİN ÜRÜN DETAY MODALI AÇ (iframe-switcher.js'ten çağrılır)
    openModalForProduct(sku) {
      console.log('[Cart.openModalForProduct] SKU:', sku);
      
      if (!sku) {
        Toast.show("Ürün kodu eksik!", "warn");
        return;
      }

      // Virgüllü SKU kontrolü (varyantlar) - Chat.openVariantPicker'a yönlendir
      if (String(sku).includes(',') || String(sku).includes('/')) {
        console.log('[Cart.openModalForProduct] Varyantlı SKU tespit edildi, Chat.openVariantPicker çağrılıyor');
        if (window.Chat?.openVariantPicker) {
          window.Chat.openVariantPicker(sku);
        } else {
          Toast.show("Varyant seçici yüklenemedi.", "warn");
        }
        return;
      }

      // SKU'yu normalize et (TİRE'yi koru!)
      const normalized = window.Data?.normalizeSku ? window.Data.normalizeSku(sku) : sku.toUpperCase().replace(/[^A-Z0-9\-]/g, '');
      const skuIndex = window.State?.skuIndex;
      
      if (!skuIndex) {
        console.error('[openModalForProduct] SKU indeksi hazır değil!');
        Toast.show("Ürün veritabanı yükleniyor...", "warn");
        return;
      }

      // Ürünü bul
      let product = skuIndex.get(normalized);
      
      // Bulunamazsa alternatif arama (TİRE'yi koru!)
      if (!product) {
        const allProducts = window.State?.products || [];
        product = allProducts.find(p => {
          const pSku = String(p.sku || '').toUpperCase().replace(/[^A-Z0-9\-]/g, '');
          return pSku === normalized;
        });
      }

      if (!product) {
        console.warn('[openModalForProduct] Ürün bulunamadı:', sku);
        Toast.show(`Ürün bulunamadı: ${sku}`, "warn");
        return;
      }

      // ÜRÜN EKLEME MODALI AÇ (adet seçimi ile)
      console.log('✅ [openModalForProduct] Ürün ekleme modalı açılıyor:', product.name);
      Cart.showAddProductModal(product);
    },

    // 🆕 PRODUCT ID İLE MODAL AÇ (brands.js ve diğer UI elemanları için)
    openProductModal(productId) {
      console.log('[Cart.openProductModal] Product ID:', productId);
      
      if (!productId) {
        Toast.show("Ürün ID eksik!", "warn");
        return;
      }

      const product = findProduct(productId);
      
      if (!product) {
        console.warn('[openProductModal] Ürün bulunamadı:', productId);
        Toast.show(`Ürün bulunamadı!`, "warn");
        return;
      }

      // Modal aç
      console.log('✅ [openProductModal] Ürün ekleme modalı açılıyor:', product.name);
      Cart.showAddProductModal(product);
    },

    // 🆕 ÜRÜN EKLEME MODALI (adet seçimi ile - sepete eklemeden önce)
    showAddProductModal(product) {
      const existingModal = document.getElementById('addProductModal');
      if (existingModal) existingModal.remove();

      const priceTxt = product.price_display || fmtTRY(priceValue(product));
      const escapeHTML = (str) => String(str).replace(/[&<>"']/g, m => ({
        '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
      }[m]));

      // Ürün resmini bul (image field veya iframe'den çek)
      const productImage = Cart._getProductImage(product);
      console.log('[Cart] Product:', product.name, 'SKU:', product.sku, 'Image:', productImage);

      const html = `
        <div class="fixed inset-0 bg-black/70 z-[9999] flex items-center justify-center p-4" 
             id="addProductModal"
             onclick="if(event.target===this) this.remove()">
          <div class="bg-gray-800 rounded-2xl w-full max-w-md border border-gray-700 shadow-2xl overflow-hidden"
               onclick="event.stopPropagation()">
            <!-- Header -->
            <div class="bg-gradient-to-r from-orange-600 to-orange-500 px-5 py-4">
              <div class="flex items-start justify-between gap-3">
                <div class="flex-1 min-w-0">
                  <h3 class="text-white font-bold text-lg leading-tight mb-1">${escapeHTML(product.name)}</h3>
                  <p class="text-orange-100 text-xs opacity-90">${escapeHTML(product.brand)} • ${escapeHTML(product.sku || '')}</p>
                </div>
                <button class="text-white/80 hover:text-white text-2xl leading-none -mt-1 flex-shrink-0" 
                        onclick="document.getElementById('addProductModal').remove()">×</button>
              </div>
            </div>

            <!-- Body -->
            <div class="p-5 space-y-4">
              ${productImage ? `
              <!-- Ürün Resmi -->
              <div class="flex justify-center bg-white rounded-xl p-4 border border-gray-600">
                <img src="${escapeHTML(productImage)}" 
                     alt="${escapeHTML(product.name)}" 
                     class="max-w-full max-h-48 object-contain"
                     onerror="this.parentElement.style.display='none'" />
              </div>
              ` : ''}

              <!-- Fiyat -->
              <div class="text-center py-3 bg-gray-700/50 rounded-xl border border-gray-600">
                <div class="text-2xl font-bold text-orange-400">${escapeHTML(priceTxt)}</div>
                <div class="text-xs text-gray-400 mt-1">Birim Fiyat</div>
              </div>

              <!-- Adet Seçimi -->
              <div class="space-y-2">
                <label class="block text-sm font-medium text-gray-300">Adet</label>
                <div class="flex items-center justify-center gap-3 bg-gray-700 rounded-xl p-2 border border-gray-600">
                  <button class="w-12 h-12 flex items-center justify-center bg-gray-800 hover:bg-gray-600 rounded-lg transition-colors text-gray-300 hover:text-white font-bold text-xl"
                          onclick="Cart._decrementQty('addProductModal')" 
                          id="btnDecrementQty">−</button>
                  <input type="number" 
                         id="productQtyInput" 
                         value="1" 
                         min="1" 
                         max="999"
                         class="w-20 text-center bg-gray-800 text-white font-bold text-xl rounded-lg border border-gray-600 py-2 focus:outline-none focus:ring-2 focus:ring-orange-500"
                         onchange="this.value = Math.max(1, Math.min(999, parseInt(this.value) || 1))" />
                  <button class="w-12 h-12 flex items-center justify-center bg-gray-800 hover:bg-gray-600 rounded-lg transition-colors text-gray-300 hover:text-white font-bold text-xl"
                          onclick="Cart._incrementQty('addProductModal')" 
                          id="btnIncrementQty">+</button>
                </div>
              </div>

              <!-- Toplam Fiyat -->
              <div class="text-center py-3 bg-gradient-to-r from-orange-600/20 to-orange-500/20 rounded-xl border border-orange-500/30">
                <div class="text-xs text-orange-300 mb-1">Toplam</div>
                <div class="text-xl font-bold text-orange-400" id="totalPrice">${escapeHTML(priceTxt)}</div>
              </div>
            </div>

            <!-- Footer -->
            <div class="p-5 pt-0 space-y-3">
              <!-- Sayfaya Git Butonu -->
              <button class="w-full bg-gradient-to-r from-blue-600/20 to-blue-500/20 hover:from-blue-600/30 hover:to-blue-500/30 text-blue-400 font-semibold py-2.5 px-4 rounded-xl transition-all border border-blue-500/30 hover:border-blue-500/50 flex items-center justify-center gap-2"
                      onclick="Cart.goToProductPage('${escapeHTML(String(product.sku || ''))}')">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
                </svg>
                Katalogda Sayfaya Git
              </button>
              
              <div class="flex gap-3">
                <button class="flex-1 bg-gray-700 hover:bg-gray-600 text-white font-semibold py-3 px-4 rounded-xl transition-colors"
                        onclick="document.getElementById('addProductModal').remove()">
                  İptal
                </button>
                <button class="flex-1 bg-gradient-to-r from-orange-600 to-orange-500 hover:from-orange-700 hover:to-orange-600 text-white font-bold py-3 px-4 rounded-xl transition-all shadow-lg hover:shadow-orange-500/30"
                        onclick="Cart._confirmAddProduct('${String(product.sku || product.id)}', '${String(product.id)}')">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="currentColor" viewBox="0 0 24 24" class="inline-block mr-1 -mt-0.5">
                    <path d="M7 18c-1.1 0-1.99.9-1.99 2S5.9 22 7 22s2-.9 2-2-.9-2-2-2zM1 2v2h2l3.6 7.59-1.35 2.45c-.16.28-.25.61-.25.96 0 1.1.9 2 2 2h12v-2H7.42c-.14 0-.25-.11-.25-.25l.03-.12.9-1.63h7.45c.75 0 1.41-.41 1.75-1.03l3.58-6.49c.08-.14.12-.31.12-.48 0-.55-.45-1-1-1H5.21l-.94-2H1zm16 16c-1.1 0-1.99.9-1.99 2s.89 2 1.99 2 2-.9 2-2-.9-2-2-2z"/>
                  </svg>
                  Sepete Ekle
                </button>
              </div>
            </div>
          </div>
        </div>
      `;

      document.body.insertAdjacentHTML('beforeend', html);

      // Adet değişimini dinle ve toplam fiyatı güncelle
      const qtyInput = document.getElementById('productQtyInput');
      const updateTotal = () => {
        const qty = parseInt(qtyInput.value) || 1;
        const total = priceValue(product) * qty;
        document.getElementById('totalPrice').textContent = fmtTRY(total);
      };
      qtyInput.addEventListener('input', updateTotal);
    },

    // Adet artır/azalt helper'ları
    _incrementQty(modalId) {
      const input = document.getElementById('productQtyInput');
      if (input) {
        const newVal = Math.min(999, parseInt(input.value) || 1) + 1;
        input.value = newVal;
        input.dispatchEvent(new Event('input'));
      }
    },

    _decrementQty(modalId) {
      const input = document.getElementById('productQtyInput');
      if (input) {
        const newVal = Math.max(1, parseInt(input.value) || 1) - 1;
        input.value = newVal;
        input.dispatchEvent(new Event('input'));
      }
    },

    // Sepete eklemeyi onayla (SKU veya ID kullan)
    _confirmAddProduct(sku, fallbackId) {
      const input = document.getElementById('productQtyInput');
      const qty = parseInt(input?.value) || 1;
      
      // SKU ile ürünü bul
      const productKey = sku || fallbackId;
      if (!productKey) {
        Toast.show("Ürün bilgisi eksik!", "warn");
        return;
      }
      
      const items = load();
      const idx = items.findIndex((x) => String(x.sku || x.id) === String(productKey));
      if (idx >= 0) {
        items[idx].qty = (items[idx].qty || 0) + qty;
      } else {
        items.push({ sku: sku, id: fallbackId, qty: qty });
      }
      save(items);
      Cart.updateBadge();
      
      const modal = document.getElementById('addProductModal');
      if (modal) modal.remove();
      
      Toast.show(`${qty} adet ürün sepete eklendi.`, "success");
    },

    // Ürün resmini bul (image field veya iframe'den otomatik çek)
    _getProductImage(product) {
      console.log('[_getProductImage] Product:', product);
      console.log('[_getProductImage] product.image:', product.image);
      
      // 1. Eğer product.image varsa direkt kullan
      if (product.image) {
        console.log('[_getProductImage] ✅ Image field bulundu:', product.image);
        return product.image;
      }

      console.log('[_getProductImage] ⚠️ Image field yok, iframe\'den deneniyor...');

      // 2. Iframe'den resmi otomatik çek
      try {
        const iframe = document.getElementById('brandFrame');
        console.log('[_getProductImage] iframe:', iframe);
        if (!iframe || !iframe.contentDocument) {
          console.log('[_getProductImage] ❌ iframe bulunamadı veya contentDocument yok');
          return null;
        }

        const iframeDoc = iframe.contentDocument;
        const sku = product.sku;
        if (!sku) {
          console.log('[_getProductImage] ❌ SKU yok');
          return null;
        }

        // SKU ile butonu bul
        const button = iframeDoc.querySelector(`button[aria-label*="${sku}"], a[href*="${sku}"]`);
        console.log('[_getProductImage] Button found:', button);
        if (!button) {
          console.log('[_getProductImage] ❌ Buton bulunamadı');
          return null;
        }

        // Butonun parent container'ını bul
        let container = button.closest('.page-content, .page, div[id^="page"], div[class*="page"]');
        if (!container) container = button.parentElement;

        // Container içindeki tüm resimleri bul (butondan önce gelenler)
        const allImages = Array.from(container.querySelectorAll('img[data-src]'));
        const buttonPosition = button.getBoundingClientRect();
        
        // Butona yakın ve butondan önce gelen resimleri filtrele
        let closestImage = null;
        let minDistance = Infinity;

        allImages.forEach(img => {
          const imgPosition = img.getBoundingClientRect();
          
          // Sadece butondan ÖNCE gelen resimleri al (Y koordinatı küçük veya aynı)
          if (imgPosition.top <= buttonPosition.top + 50) {
            const distance = Math.abs(buttonPosition.top - imgPosition.top) + 
                           Math.abs(buttonPosition.left - imgPosition.left);
            
            // Ürün resmi olabilecek boyuttaki resimleri filtrele
            const width = img.naturalWidth || parseInt(img.getAttribute('width')) || 0;
            const height = img.naturalHeight || parseInt(img.getAttribute('height')) || 0;
            
            // Çok küçük resimleri (icon, logo vb) atla
            if (width > 50 && height > 50 && distance < minDistance) {
              minDistance = distance;
              closestImage = img;
            }
          }
        });

        if (closestImage) {
          const src = closestImage.getAttribute('data-src') || closestImage.src;
          console.log('[_getProductImage] ✅ Closest image src:', src);
          if (src && !src.includes('blank.gif')) {
            // Göreceli yolu iframe URL'ine göre düzenle
            const iframeURL = iframe.src;
            const baseURL = iframeURL.substring(0, iframeURL.lastIndexOf('/') + 1);
            const finalURL = src.startsWith('http') ? src : baseURL + src;
            console.log('[_getProductImage] ✅ Final image URL:', finalURL);
            return finalURL;
          }
        }
        
        console.log('[_getProductImage] ❌ Uygun resim bulunamadı');
      } catch (error) {
        console.error('[_getProductImage] ❌ Error:', error);
      }

      return null;
    }
  };

  window.Cart = Cart;
  document.addEventListener("DOMContentLoaded", Cart.updateBadge);

  // === postMessage entegrasyonu (TEK KAYNAK) ===
  (function () {
    function findBySkuToken(tok) {
      const k = window.Data?.normalizeSku ? window.Data.normalizeSku(tok) : String(tok);
      return window.State?.skuIndex?.get(k) || null;
    }
    function uniqueById(arr) {
      const seen = new Set();
      return arr.filter((p) => {
        const id = String(p.id);
        if (seen.has(id)) return false;
        seen.add(id);
        return true;
      });
    }
    function openVariantPicker(products) {
      const items = products
        .map((p) => {
          const price = p.price_display || window.Price?.formatTRY?.(p.price) || "";
          const sku = p.sku || "";
          return `
        <div class="border border-gray-700 rounded-lg p-3">
          <div class="flex justify-between items-start gap-3">
            <div class="flex-1">
              <h4 class="text-sm text-white font-medium">${(p.name || "").replace(/&/g, "&amp;")}</h4>
              <p class="text-xs text-gray-400">${p.brand || ""} • ${sku || ""}</p>
              ${price ? `<p class="text-sm text-orange-500 font-semibold mt-1">${price}</p>` : ``}
            </div>
            <button class="bg-orange-600 hover:bg-orange-700 text-white text-xs font-medium px-3 py-1.5 rounded"
                    onclick="Cart.quickAdd('${String(p.id)}'); document.getElementById('variantModal').remove();">
              Sepete Ekle
            </button>
          </div>
        </div>`;
        })
        .join("");

      const html = `
        <div class="fixed inset-0 bg-black/60 z-50 flex items-center justify-center" id="variantModal">
          <div class="bg-gray-800 rounded-xl p-5 w-[28rem] max-w-[95vw] border border-gray-700">
            <div class="flex justify-between mb-3">
              <h3 class="text-white font-semibold">Varyasyon Seç</h3>
              <button class="text-gray-400 hover:text-white" onclick="document.getElementById('variantModal').remove()">✕</button>
            </div>
            <div class="space-y-2 max-h-[60vh] overflow-y-auto">${items}</div>
          </div>
        </div>`;
      document.body.insertAdjacentHTML("beforeend", html);
    }

    // postMessage listener removed - now handled by main.js setupIframeListener()
    // This prevents duplicate modal openings when InDesign SEPET buttons are clicked
  })();

  // ============ GLOBAL addToCart KALDırıLDI ============
  // Artık iframe'ler parent-bridge.js üzerinden postMessage kullanıyor
  // iframe-switcher.js bu mesajları yakalar ve Cart.openModalForProduct() çağırır
  // Modal içindeki "Sepete Ekle" butonu ürünü sepete ekler

})();
