/* The optional online overlay of the demo layer (added 8 Oct 2026).
   scripts/06_build_layer.py writes this beside index.html as overlay.js, filled in from scripts/layer_overlay.json - and only
   if that file registers a documented endpoint, with its terms, its version and its attribution.
   The page loads overlay.js ONLY when its user ticks the overlay. Nothing in index.html or data.js asks the network for
   anything: this file is the one place that can. Delete it and the map is exactly the offline map. */
window.ICTD_OVERLAY = {
  url: __URL__,
  attribution: __ATTRIBUTION__,
  version: __VERSION__,
  make: function (L, pane, firstYear, lastYear) {   // the years of the window chosen for the decision view
    return L.tileLayer(this.url + "&start_year=" + firstYear + "&end_year=" + lastYear, { pane: pane, opacity: 0.85, minZoom: 6, maxZoom: 15, maxNativeZoom: __MAX_NATIVE_ZOOM__, attribution: this.attribution });
  }
};
