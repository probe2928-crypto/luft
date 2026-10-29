/* LUFT 앱 셸 — 사이트 화면 위에 네이티브 기능을 얹는다.
   뒤로가기(안드로이드), 상품 공유(시스템 공유 창), 담기 진동, 외부 링크는 앱 안 브라우저로,
   실결제가 켜지면 결제만 앱 안 브라우저(사이트 결제 화면)로 넘김 — 카드사 앱 전환·토스 인증이 웹뷰보다 안정적.
   실물 상품 판매라 애플·구글 인앱결제 대상이 아님(실물 상품·서비스 예외). */
(function () {
  var C = window.Capacitor, native = !!(C && C.isNativePlatform && C.isNativePlatform());
  var P = (C && C.Plugins) || {};
  var I = window.LUFT_APP_INFO || {};
  var H = document.documentElement, REMOTE = I.remote || "https://probe2928-crypto.github.io/luft/";
  H.classList.add("luft-app");
  if (native) H.classList.add("luft-native", "luft-" + ((C.getPlatform && C.getPlatform()) || "app"));

  function haptic() { try { if (native && P.Haptics) P.Haptics.impact({ style: "LIGHT" }); } catch (e) {} }
  function openUrl(url) {
    if (native && P.Browser) return P.Browser.open({ url: url, toolbarColor: "#141210", presentationStyle: "fullscreen" });
    window.open(url, "_blank", "noopener");
  }
  function b64u(s) { return btoa(unescape(encodeURIComponent(s))).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, ""); }

  // 화면 아래 작은 안내 띠 (버튼 1개까지)
  function note(msg, btn, fn) {
    var n = document.getElementById("appNote");
    if (!n) { n = document.createElement("div"); n.id = "appNote"; n.className = "app-note"; n.setAttribute("role", "status"); document.body.appendChild(n); }
    n.innerHTML = "";
    var t = document.createElement("span"); t.textContent = msg; n.appendChild(t);
    if (btn) { var b = document.createElement("button"); b.type = "button"; b.textContent = btn; b.onclick = function () { n.classList.remove("on"); fn && fn(); }; n.appendChild(b); }
    var x = document.createElement("button"); x.type = "button"; x.className = "x"; x.setAttribute("aria-label", "닫기"); x.textContent = "×"; x.onclick = function () { n.classList.remove("on"); }; n.appendChild(x);
    requestAnimationFrame(function () { n.classList.add("on"); });
    clearTimeout(note._t); if (!btn) note._t = setTimeout(function () { n.classList.remove("on"); }, 4200);
  }

  var A = window.LUFT_APP = {
    touched: false,
    note: note,
    // 사이트의 route()가 #checkout에서 부름 (실결제 모드일 때만). true면 사이트는 결제 화면을 그리지 않음
    checkout: function (cart) {
      if (!cart || !cart.length) return false;
      openUrl(REMOTE + "?cart=" + b64u(JSON.stringify(cart)) + "&from=app#checkout");
      A.paying = true;
      history.replaceState(null, "", "#cart");
      setTimeout(function () { window.dispatchEvent(new HashChangeEvent("hashchange")); }, 0);
      return true;
    }
  };

  // 앱 안 브라우저를 닫고 돌아왔을 때: 결제했으면 장바구니 비우기
  if (native && P.Browser && P.Browser.addListener) P.Browser.addListener("browserFinished", function () {
    if (!A.paying) return; A.paying = false;
    note("결제를 마쳤다면 장바구니를 비울게요. 주문은 고객센터 → 주문 조회에서 확인돼요.", "비우기", function () {
      try { localStorage.setItem("luft-cart", "[]"); } catch (e) {}
      location.hash = "home"; location.reload();
    });
  });

  // 외부 링크: 앱 안 브라우저로 (전화·메일은 기기 앱으로)
  document.addEventListener("click", function (e) {
    A.touched = true;
    var a = e.target.closest && e.target.closest("a[href]");
    if (a) {
      var href = a.getAttribute("href") || "";
      if (/^https?:\/\//i.test(href) && a.host !== location.host) { e.preventDefault(); openUrl(a.href); return; }
    }
    var b = e.target.closest && e.target.closest("[data-qa], #sbBtn, #addBtn, .pd-buy .cta, #buyNow, #appShare");
    if (b) haptic();
  }, true);

  // 상품 화면에 '공유' 버튼
  function share(id, name) {
    var url = REMOTE + "#p-" + id, title = "LUFT · " + name;
    if (native && P.Share) return P.Share.share({ title: title, text: title, url: url, dialogTitle: "공유하기" }).catch(function () {});
    if (navigator.share) return navigator.share({ title: title, url: url }).catch(function () {});
    try { navigator.clipboard.writeText(url); note("링크를 복사했어요"); } catch (e) {}
  }
  function decorate() {
    var h = location.hash.slice(1);
    if (h.indexOf("p-") !== 0) return;
    var id = h.slice(2), box = document.querySelector(".pd-buy");
    if (!box || document.getElementById("appShare")) return;
    var cat = window.LUFT_CATALOG || {}, p = (cat.products || {})[id]; if (!p) return;
    var b = document.createElement("button");
    b.type = "button"; b.id = "appShare"; b.className = "app-share mono"; b.textContent = "공유하기";
    b.onclick = function () { share(id, p.ko || p.name || id); };
    box.appendChild(b);
  }
  addEventListener("hashchange", function () { setTimeout(decorate, 60); });
  addEventListener("load", function () { setTimeout(decorate, 120); });

  // 아래 탭 (홈 · 샵 · 장바구니 · 고객센터) — 위쪽 메뉴는 앱에서 숨김
  var TABS = [["home", "홈", '<path d="M3 11.5 12 4l9 7.5V20a1 1 0 0 1-1 1h-5v-6h-6v6H4a1 1 0 0 1-1-1z"/>'],
    ["shop", "샵", '<rect x="4" y="4" width="7" height="7" rx="1"/><rect x="13" y="4" width="7" height="7" rx="1"/><rect x="4" y="13" width="7" height="7" rx="1"/><rect x="13" y="13" width="7" height="7" rx="1"/>'],
    ["cart", "장바구니", '<path d="M5 7h14l-1.2 11.2a2 2 0 0 1-2 1.8H8.2a2 2 0 0 1-2-1.8z"/><path d="M9 7V6a3 3 0 0 1 6 0v1"/>'],
    ["help", "고객센터", '<circle cx="12" cy="12" r="8.5"/><path d="M9.6 9.5a2.5 2.5 0 1 1 3.4 2.3c-.6.3-1 .8-1 1.5v.5"/><circle cx="12" cy="17" r=".6" fill="currentColor"/>']];
  function tabbar() {
    if (document.getElementById("appTabs")) return;
    var nav = document.createElement("nav"); nav.id = "appTabs"; nav.className = "app-tabs"; nav.setAttribute("aria-label", "메뉴");
    nav.innerHTML = TABS.map(function (t) {
      return '<a href="#' + t[0] + '" data-tab="' + t[0] + '"><svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round">' + t[2] + '</svg><span>' + t[1] + (t[0] === "cart" ? ' <b id="appCartN"></b>' : "") + "</span></a>";
    }).join("");
    document.body.appendChild(nav);
    nav.addEventListener("click", function (e) {
      var a = e.target.closest("a[data-tab]"); if (!a) return;
      haptic();
      if (location.hash === "#" + a.dataset.tab) { e.preventDefault(); window.scrollTo({ top: 0, behavior: "smooth" }); }
    });
    sync();
  }
  function sync() {
    var h = (location.hash || "#home").slice(1), cur = /^(cart|checkout)$/.test(h) ? "cart" : /^help/.test(h) ? "help" : /^(shop|sets|p-)/.test(h) ? "shop" : "home";
    document.querySelectorAll("#appTabs a").forEach(function (a) { a.classList.toggle("on", a.dataset.tab === cur); if (a.dataset.tab === cur) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current"); });
    var c = document.getElementById("cartCount"), n = document.getElementById("appCartN");
    if (c && n) { n.textContent = c.textContent !== "0" ? c.textContent : ""; }
  }
  addEventListener("hashchange", sync);
  document.addEventListener("DOMContentLoaded", function () {
    tabbar();
    var c = document.getElementById("cartCount");
    if (c && window.MutationObserver) new MutationObserver(sync).observe(c, { childList: true, characterData: true, subtree: true });
  });

  // 오프라인 안내
  addEventListener("offline", function () { note("인터넷 연결이 끊겼어요. 상품은 볼 수 있지만 주문·결제는 연결 후에 돼요."); });

  if (!native) return;
  // 안드로이드 뒤로가기: 열린 창 닫기 → 이전 화면 → 첫 화면에선 앱 종료
  if (P.App) P.App.addListener("backButton", function () {
    var n = document.getElementById("appNote");
    if (n && n.classList.contains("on")) { n.classList.remove("on"); return; }
    var h = location.hash.replace(/^#/, "");
    if (h && h !== "home") history.back(); else P.App.exitApp();
  });
  try { P.StatusBar && P.StatusBar.setStyle({ style: "DARK" }); } catch (e) {}
  addEventListener("load", function () { setTimeout(function () { try { P.SplashScreen && P.SplashScreen.hide({ fadeOutDuration: 250 }); } catch (e) {} }, 150); });
})();
