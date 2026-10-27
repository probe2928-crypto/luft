// LUFT 결제 설정. 두 값이 모두 채워지면 실결제(토스 결제위젯)가 켜지고, 비어 있으면 미리보기 모드예요.
// apiBase: 주문 서버(Cloudflare Worker) 주소. 예: "https://luft-orders.내계정.workers.dev"
// tossClientKey: 토스페이먼츠 결제위젯 '클라이언트 키' (test_gck_... 또는 live_gck_...). 시크릿 키는 절대 여기 넣지 마세요.
window.LUFT_CONFIG = {
  apiBase: "",
  tossClientKey: ""
};
