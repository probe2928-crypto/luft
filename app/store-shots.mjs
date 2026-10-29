// 스토어 이미지: app/www 를 앱 모드 그대로 띄워 찍는다 (GitHub Actions: .github/workflows/store-shots.yml)
// iPhone 6.9" 1320×2868, Google Play 휴대폰 1080×1920, Play 피처 그래픽 1024×500, 아이콘 512/1024
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

const APP = path.dirname(fileURLToPath(import.meta.url));
const WWW = path.join(APP, "www"), OUT = path.join(APP, "store");
fs.mkdirSync(OUT, { recursive: true });
const TYPES = { ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".css": "text/css", ".jpg": "image/jpeg", ".png": "image/png", ".svg": "image/svg+xml", ".webp": "image/webp" };
const srv = http.createServer((q, r) => {
  const p = path.join(WWW, decodeURIComponent(q.url.split("?")[0]).replace(/^\/$/, "/index.html"));
  if (!p.startsWith(WWW) || !fs.existsSync(p)) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { "content-type": TYPES[path.extname(p)] || "application/octet-stream" }); fs.createReadStream(p).pipe(r);
}).listen(4610);

const cat = JSON.parse(fs.readFileSync(path.join(WWW, "catalog.js"), "utf8").replace(/^[^{]*/, "").replace(/;\s*$/, ""));
const firstColl = cat.collections[0], pid = firstColl.ids[0], p2 = firstColl.ids[1] || pid;
const cart = [{ id: pid, opt: cat.products[pid].opts?.[0] || "", q: 1 }, { id: p2, opt: cat.products[p2].opts?.[0] || "", q: 1 }];
const SHOTS = [["01-home", "#home"], ["02-product", "#p-" + pid], ["03-shop", "#shop"], ["04-cart", "#cart"], ["05-help", "#help"]];

const b = await chromium.launch();
for (const [kind, w, h, scale] of [["ios", 440, 956, 3], ["play", 360, 640, 3]]) {
  const ctx = await b.newContext({ viewport: { width: w, height: h }, deviceScaleFactor: scale, locale: "ko-KR", isMobile: true, hasTouch: true });
  await ctx.addInitScript((c) => { try { localStorage.setItem("luft-cart", JSON.stringify(c)); } catch (e) {} }, cart);
  await ctx.route(/probe2928-crypto\.github\.io\/luft\/(catalog|config)\.js/, (r) => r.abort());   // 앱에 든 목록 그대로
  const pg = await ctx.newPage();
  await pg.goto("http://localhost:4610/index.html#home", { waitUntil: "networkidle" }); await pg.waitForTimeout(1500);
  for (const [name, hash] of SHOTS) {
    await pg.evaluate((x) => { location.hash = x; }, hash); await pg.waitForTimeout(1800);
    await pg.evaluate((n) => {
      if (n === "03-shop") { const el = document.getElementById("shop"); if (el) window.scrollTo(0, el.getBoundingClientRect().top + scrollY - 70); }
      else if (n === "02-product") { const el = document.querySelector(".pd-buy"); if (el) window.scrollTo(0, el.getBoundingClientRect().top + scrollY - 90); }
      else window.scrollTo(0, 0);
    }, name); await pg.waitForTimeout(700);
    await pg.screenshot({ path: `${OUT}/${kind}-${name}.png` });
    console.log(kind, name);
  }
  await ctx.close();
}
// 피처 그래픽 + 아이콘
const f = await b.newPage({ viewport: { width: 1024, height: 500 } });
const img = "data:image/jpeg;base64," + fs.readFileSync(path.join(WWW, cat.products[pid].img)).toString("base64");
await f.setContent(`<html><head><link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,800&family=IBM+Plex+Sans+KR:wght@500&display=swap" rel="stylesheet"></head>
<body style="margin:0;width:1024px;height:500px;background:#F1C7A6;overflow:hidden;position:relative;font-family:'IBM Plex Sans KR',sans-serif">
<div style="position:absolute;left:56px;top:0;bottom:0;display:flex;flex-direction:column;justify-content:center;color:#141210">
<div style="font-family:Archivo,sans-serif;font-stretch:70%;font-weight:800;font-size:170px;line-height:.85;letter-spacing:-.02em">LUFT</div>
<div style="margin-top:22px;font-size:26px">서울 컬렉션 · 내 이름을 새기는 케이스</div>
<div style="margin-top:8px;font:500 15px/1 monospace;letter-spacing:.2em;opacity:.7">SEOUL COLLECTION · MADE TO ORDER</div></div>
<img src="${img}" style="position:absolute;right:40px;top:-10px;height:520px;object-fit:contain"></body></html>`, { waitUntil: "networkidle" });
await f.waitForTimeout(800); await f.screenshot({ path: `${OUT}/play-feature-graphic.png` });
const icon = "data:image/png;base64," + fs.readFileSync(path.join(APP, "resources", "icon-only.png")).toString("base64");
for (const [file, px] of [["appstore-icon-1024.png", 1024], ["play-icon-512.png", 512]]) {
  const ic = await b.newPage({ viewport: { width: px, height: px } });
  await ic.setContent(`<body style="margin:0"><img src="${icon}" style="width:${px}px;height:${px}px;display:block"></body>`, { waitUntil: "load" });
  await ic.screenshot({ path: `${OUT}/${file}` }); await ic.close();
}
await b.close(); srv.close();
console.log("done →", OUT);
