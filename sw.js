// LUFT 웹앱 오프라인 기본 처리: 화면(index)·카탈로그는 네트워크 우선, 이미지는 캐시 우선. 결제·외부 요청은 건드리지 않음.
const V='luft-v20261108e';
const CORE=['./','./index.html','./catalog.js','./config.js','./manifest.webmanifest','./img/icons/icon-192.png','./img/scent/jar-pine.webp','./img/scent/jar-yuzu.webp','./img/scent/jar-tea.webp'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(V).then(c=>c.addAll(CORE)).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==V).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',e=>{const r=e.request,u=new URL(r.url);
 if(r.method!=='GET'||u.origin!==location.origin||/\.mp4$/.test(u.pathname))return;   // 영상은 SW를 거치지 않음(iOS Range 요청)
 if(/\.(jpg|jpeg|png|webp|mp4)$/.test(u.pathname)){e.respondWith(caches.match(r).then(m=>m||fetch(r).then(res=>{if(res.ok&&!/\.mp4$/.test(u.pathname)){const cp=res.clone();caches.open(V).then(c=>c.put(r,cp))}return res})));return}
 e.respondWith(fetch(r).then(res=>{if(res.ok){const cp=res.clone();caches.open(V).then(c=>c.put(r,cp))}return res}).catch(()=>caches.match(r).then(m=>m||caches.match('./index.html'))));
});
