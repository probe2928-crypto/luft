/* LUFT 앱: 상품 목록(catalog.js) 최신화
   - 앱에는 빌드할 때의 catalog.js가 들어 있고, 실행할 때마다 사이트의 catalog.js를 받아 다르면 저장해 두었다가 씀
   - 사이트에만 있는 새 상품 이미지(img/...)는 사이트 주소에서 불러옴
   - 원격 파일은 JSON으로만 읽고 코드로 실행하지 않음 */
(function () {
  var I = window.LUFT_APP_INFO || {}, KEY = "luft-app-catalog", launched = Date.now();
  var B = {}; (I.bundled || []).forEach(function (f) { B[f] = 1; });
  var cat = window.LUFT_CATALOG;
  try {
    var s = JSON.parse(localStorage.getItem(KEY) || "null");
    // 저장본은 이 앱 빌드 뒤에 받은 것만 씀 (앱을 새로 깔면 앱에 든 목록이 우선)
    if (s && s.cat && s.cat.products && s.at > (I.built || "")) cat = window.LUFT_CATALOG = s.cat;
  } catch (e) {}
  var shown = JSON.stringify(cat || {});   // 지금 화면에 쓰는 목록 (이미지 주소 바꾸기 전)

  function fix(v) {
    if (typeof v === "string") return /^img\//.test(v) && !B[v] ? (I.remote || "") + v : v;
    if (Array.isArray(v)) return v.map(fix);
    return v;
  }
  if (cat && cat.products) Object.keys(cat.products).forEach(function (id) {
    var p = cat.products[id];
    Object.keys(p).forEach(function (k) { if (/^(img|imgs|gallery|photos)$/.test(k)) p[k] = fix(p[k]); });
  });

  function parse(text) {
    var a = text.indexOf("{"), b = text.lastIndexOf("}");
    if (a < 0 || b < a) return null;
    try { var j = JSON.parse(text.slice(a, b + 1)); return j && j.products && j.collections ? j : null; } catch (e) { return null; }
  }
  function refresh() {
    if (!I.remote || navigator.onLine === false) return;
    fetch(I.remote + "catalog.js?t=" + Date.now(), { cache: "no-store" }).then(function (r) { return r.ok ? r.text() : ""; }).then(function (t) {
      var j = t && parse(t); if (!j) return;
      if (JSON.stringify(j) === shown) return;
      try { localStorage.setItem(KEY, JSON.stringify({ at: new Date().toISOString(), cat: j })); } catch (e) { return; }
      var A = window.LUFT_APP || {};
      // 앱을 막 켰고 아직 아무것도 안 눌렀으면 바로 새로 그림, 아니면 다음 실행 때
      if (Date.now() - launched < 6000 && !A.touched) location.reload();
      else if (A.note) A.note("새 상품이 들어왔어요. 앱을 다시 열면 보여요.");
    }).catch(function () {});
  }
  if (document.readyState === "complete") setTimeout(refresh, 200); else addEventListener("load", function () { setTimeout(refresh, 200); });
})();
