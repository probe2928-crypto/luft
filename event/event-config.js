/* LUFT 가입 혜택(웰컴 쿠폰) 설정 — 계획·근거: chainbrief ops/events/PLAN.md
   enabled:true = 공개. 로그인(site-auth) + ops/events/schema.sql + 결제 Worker 의 쿠폰 검증(PLAN.md §5)이 준비된 뒤에만 켠다.
   쿠폰 금액·조건은 화면 문구일 뿐, 실제 할인액은 결제 Worker 가 서버에서 다시 계산한다. 미리보기: 로컬에서 ?event_preview=1 */
window.SITE_EVENT = {
  enabled: false,
  site: "luft",
  lang: "ko",
  kind: "welcome",
  id: "luft-welcome",
  rulesUrl: document.currentScript ? document.currentScript.src.replace(/event-config\.js.*$/, "") : "event/",
  versions: { rules: "2026-11-02", consent: "ev-2026-11-02", marketing: "2026-11-02" },
  width: "1280px",
  theme: { ink: "#141210", paper: "#FBF6F1", accent: "#141210", muted: "#4A433D", line: "rgba(20,18,16,.16)", wash: "#F1C7A6", radius: "0px",
           font: '"IBM Plex Sans KR","Apple SD Gothic Neo",sans-serif', display: '"Archivo","Arial Narrow",Arial,sans-serif', dw: "800" },
  banner: {
    mount: "header.top",
    where: "afterend",
    figure: "₩2,000",
    figureNote: "WELCOME COUPON",
    title: "가입하면 첫 주문 2,000원 할인",
    body: "14,900원 이상 첫 주문에 쓸 수 있어요. 가입 후 30일 동안, 1인 1회.",
    cta: "쿠폰 받기",
    label: "가입 혜택"
  },
  welcome: {
    title: "웰컴 쿠폰 2,000원",
    points: ["14,900원 이상 첫 주문에 사용", "가입 후 30일 안에, 1인 1회", "다른 쿠폰과 함께 쓸 수 없어요"],
    note: "가입은 무료예요. 가입하면 이 페이지에서 바로 받을 수 있어요.",
    done: function (d) { return "쿠폰 " + (d.code || "") + " 이 내 계정에 들어왔어요. 결제할 때 자동으로 적용돼요."; }
  }
};
(function () {
  var C = window.SITE_EVENT, local = /^(localhost|127\.0\.0\.1)$/.test(location.hostname);
  if (!C.enabled && !(local && /[?&]event_preview=1(&|$)/.test(location.search)) && !document.documentElement.hasAttribute("data-event-page")) return;
  var s = document.createElement("script"); s.src = (document.currentScript && document.currentScript.src || "").replace(/event-config\.js.*$/, "event.js"); s.defer = true; document.head.appendChild(s);
})();
