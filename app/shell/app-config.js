/* LUFT 앱: 결제 설정(config.js) 최신화
   사이트 config.js에 토스 클라이언트 키·주문 서버 주소가 채워지면 앱도 다음 실행부터 실결제 모드로 바뀜.
   (클라이언트 키는 공개용 값이라 앱에 저장해도 됨. 시크릿 키는 어디에도 넣지 않음) */
(function () {
  var I = window.LUFT_APP_INFO || {}, KEY = "luft-app-config";
  try {
    var s = JSON.parse(localStorage.getItem(KEY) || "null");
    if (s && s.at > (I.built || "") && s.cfg) window.LUFT_CONFIG = { apiBase: s.cfg.apiBase || "", tossClientKey: s.cfg.tossClientKey || "" };
  } catch (e) {}
  function pick(t, k) { var m = t.match(new RegExp(k + "\\s*:\\s*[\"']([^\"']*)[\"']")); return m ? m[1] : ""; }
  function refresh() {
    if (!I.remote || navigator.onLine === false) return;
    fetch(I.remote + "config.js?t=" + Date.now(), { cache: "no-store" }).then(function (r) { return r.ok ? r.text() : ""; }).then(function (t) {
      if (!t || t.indexOf("LUFT_CONFIG") < 0) return;
      var cfg = { apiBase: pick(t, "apiBase"), tossClientKey: pick(t, "tossClientKey") };
      if (cfg.apiBase && !/^https:\/\//.test(cfg.apiBase)) return;
      if (cfg.tossClientKey && !/^(test|live)_[a-z]+_[A-Za-z0-9]+$/.test(cfg.tossClientKey)) return;
      try { localStorage.setItem(KEY, JSON.stringify({ at: new Date().toISOString(), cfg: cfg })); } catch (e) {}
    }).catch(function () {});
  }
  if (document.readyState === "complete") setTimeout(refresh, 400); else addEventListener("load", function () { setTimeout(refresh, 400); });
})();
