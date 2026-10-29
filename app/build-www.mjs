// 사이트(../index.html · catalog.js · config.js · img/)를 앱 화면(www/)으로 옮긴다.
// 앱에서만 바뀌는 것:
//  - app-shell.js: 네이티브 기능(뒤로가기·공유·진동·외부 링크·결제는 브라우저로)
//  - app-catalog.js / app-config.js: 사이트에 새 상품·결제 설정이 올라오면 앱을 다시 내지 않아도 반영
//  - 자매 사이트 배너(network.js)는 앱에서 뺌 (코인 사이트·거래소 링크가 쇼핑 앱에 들어가지 않게)
// 인쇄용 원본(print/), 제작처 자료(oem/)는 앱에 넣지 않는다.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const APP = path.dirname(fileURLToPath(import.meta.url));
const SITE = path.resolve(process.env.LUFT_SITE || path.join(APP, ".."));
const OUT = path.join(APP, "www");
const REMOTE = "https://probe2928-crypto.github.io/luft/";

fs.rmSync(OUT, { recursive: true, force: true });
fs.mkdirSync(OUT, { recursive: true });
for (const f of ["catalog.js", "config.js"]) fs.copyFileSync(path.join(SITE, f), path.join(OUT, f));
fs.cpSync(path.join(SITE, "img"), path.join(OUT, "img"), { recursive: true });
for (const f of fs.readdirSync(path.join(APP, "shell"))) fs.copyFileSync(path.join(APP, "shell", f), path.join(OUT, f));

// 앱에 들어간 이미지 목록 — 사이트에만 있는 새 상품 이미지는 온라인 주소로 불러온다
const bundled = fs.readdirSync(path.join(OUT, "img")).map((f) => "img/" + f);
const built = new Date().toISOString();
fs.writeFileSync(path.join(OUT, "app-manifest.js"),
  `window.LUFT_APP_INFO=${JSON.stringify({ remote: REMOTE, built, bundled })};\n`);

let html = fs.readFileSync(path.join(SITE, "index.html"), "utf8");
const swap = (a, b) => {
  if (!html.includes(a)) throw new Error("사이트 index.html 구조가 바뀌었어요 (못 찾음): " + a);
  html = html.replace(a, b);
};
swap('<script src="catalog.js"></script>',
  '<script src="app-manifest.js"></script><script src="catalog.js"></script><script src="app-catalog.js"></script>' +
  '<link rel="stylesheet" href="app-shell.css"><script src="app-shell.js"></script>');
swap('<script src="config.js"></script>', '<script src="config.js"></script><script src="app-config.js"></script>');
html = html.replace(/<script src="https:\/\/probe2928-crypto\.github\.io\/chainbrief\/network\.js"[^>]*><\/script>\s*/, "");
html = html.replace("<title>LUFT Store</title>", "<title>LUFT</title>");
html = html.replace('<meta name="claude:viewport-fit-sides" content="cover">', "");
fs.writeFileSync(path.join(OUT, "index.html"), html);

const size = (d) => fs.readdirSync(d, { withFileTypes: true }).reduce((a, e) => a + (e.isDirectory() ? size(path.join(d, e.name)) : fs.statSync(path.join(d, e.name)).size), 0);
console.log(`www 준비 완료: 이미지 ${bundled.length}개, ${(size(OUT) / 1e6).toFixed(1)}MB, ${built}`);
