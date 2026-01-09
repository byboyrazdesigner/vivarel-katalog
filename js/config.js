// /js/config.js  (v13) — central brand routing & runtime flags
window.Config = window.Config || {};

// Turn off iframe usage for brand pages.
window.Config.USE_IFRAME = false;

// Default brand if none can be inferred
window.Config.DEFAULT_BRAND = "ZONE_DENMARK";

// Brand folder mapping (exact folder names under /Markalar)
window.Config.BRAND_PATHS = {
  "ZONE":                  "/Markalar/ZONE_DENMARK/index.html",  // Fallback for products.json
  "ZONE_DENMARK":          "/Markalar/ZONE_DENMARK/index.html",
  "ZONE_DENMARK_MUTFAK":   "/Markalar/ZONE_DENMARK_MUTFAK/index.html",
  "ZONE_DENMARK_BANYO":    "/Markalar/ZONE_DENMARK_BANYO/index.html",
  "STUDIO_ROUND":          "/Markalar/StudioGround/index.html",
};

// Brand order (optional)
window.Config.BRAND_ORDER = [
  "ZONE_DENMARK",
  "ZONE_DENMARK_MUTFAK",
  "ZONE_DENMARK_BANYO",
  "ARIT",
  "BAOLGI",
  "Bitz",
  "Foppapedretti",
  "GEFU",
  "Gense",
  "Hailo",
  "Le Feu",
  "Lyngby Glas",
  "Rosti",
  "STUDIO_ROUND",
  "Umbra",
  "Villa Collection",
  "Yamazaki",
  "TEM"
];

// Resolve brand -> src path robustly
window.Config.brandToSrc = function brandToSrc(brand) {
  if (!brand) return window.Config.BRAND_PATHS[window.Config.DEFAULT_BRAND];
  const map = window.Config.BRAND_PATHS;
  if (map[brand]) return map[brand];
  const key = Object.keys(map).find(k => String(k).toLowerCase() === String(brand).toLowerCase());
  if (key) return map[key];
  const guess = "/Markalar/" + String(brand).replace(/\s+/g,'') + "/index.html";
  return guess;
};
