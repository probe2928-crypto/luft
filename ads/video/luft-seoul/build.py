#!/usr/bin/env python3
"""Builds the two aspect ratios of the LUFT Seoul ad from src/template.html.

  python3 build.py   -> index.html (9:16) + ../luft-seoul-16x9/index.html (16:9)

Everything is laid out inside a 1080x1080 "core" that is centred horizontally;
in 9:16 the core sits high (top 240) so all words stay inside the 168-1330 px band.
"""
import math, sys, pathlib

ROOT = pathlib.Path(__file__).parent
DUR = 20.0
LAND_CSS = """
#s2-caps{left:-300px;top:400px;width:520px;height:300px}
.cap2{top:0;width:520px;flex-direction:column;align-items:flex-start;justify-content:flex-start;gap:12px}
.cap2 .n{font-size:28px}
.cap2 .t{font-size:76px;line-height:1.12}
#s5-card{left:-360px;top:70px;width:600px}
#s4-cap{left:-430px;width:1040px;text-align:right}
#s7-big{font-size:500px;top:250px;left:-340px;width:auto;justify-content:flex-start}
#s7-cta{left:-340px;width:auto;justify-content:flex-start}
#sp1,#sp2{flex-direction:row;right:auto !important;left:1045px}
#sp1 i,#sp2 i{transform-origin:0 50%}
"""

def build(fmt):
    P = fmt == "portrait"
    if P:
        W, H, OX, OY, res, out = 1080, 1920, 0, 240, "portrait", "index.html"
    else:
        W, H, OX, OY, res, out = 1920, 1080, 420, 0, "landscape", "../luft-seoul-16x9/index.html"
    hero_s = 1.0 if P else 0.86
    hero_top = -22 if P else -2.5
    end_sc = 0.5769 if P else 0.62
    ecw, ech = round(520 * end_sc), round(1045 * end_sc)
    ecy = 380 if P else 216
    seal_y = ecy + 80.5 * end_sc
    push_ty = 280
    tokens = dict(
        W=W, H=H, OX=OX, OY=OY, RES=res, DUR=DUR, S7DUR=round(DUR - 17.1, 2),
        LAND=0 if P else 1,
        GLOWY=round((OY + 480) / H * 100, 1),
        IRISX=OX + 803, IRISY=OY + 725, IRISR=int(math.hypot(W, H)) + 40,
        PHONE_SCALE=1.36 if P else 1.0, PHONE_TX=0 if P else 250,
        RING_S=1.22 if P else 1.0, RING_Y=560 if P else 520, NAMES_Y=960 if P else 880,
        HERO_S=hero_s, HERO_TOP=hero_top, HERO_CY=round(hero_top + 522.5, 1),
        PUSH_S=3.6, PUSH_TY=push_ty, PUSH_TX=540 if P else 600, LEAD_X=539 if P else 599,
        DOF_TOP=push_ty + 150, LEAD_Y=push_ty + 146, LEAD_H=60, S4CAP_Y=push_ty + 222,
        MAPCARD_Y=0, SWOOSH_Y=792,
        END_SC=end_sc, ENDCASE_W=ecw, ENDCASE_H=ech, ENDCASE_X=round((540 if P else 870) - ecw / 2), ENDCASE_Y=ecy,
        CTA_Y=1000 if P else 690,
        SP_R=round((540 if P else 870) + ecw / 2 + 14), SP_LR=round(1080 - (540 - ecw / 2 - 14)),
        SP3_Y=round(seal_y - 24), SP4_Y=round(ecy + ech * .36), SP5_Y=round(ecy + ech * .52),
        SP1_Y=round(ecy + ech * (.12 if P else .68)), SP2_Y=round(ecy + ech * (.62 if P else .80)),
        EXTRA_CSS="" if P else LAND_CSS,
    )
    html = (ROOT / "src/template.html").read_text()
    for k, v in tokens.items():
        html = html.replace("{{" + k + "}}", str(v))
    assert "{{" not in html, html[html.index("{{"):html.index("{{") + 40]
    (ROOT / out).parent.mkdir(exist_ok=True)
    (ROOT / out).write_text(html)
    print("wrote", out, W, "x", H)

if __name__ == "__main__":
    for fmt in ("portrait", "landscape"):
        build(fmt)
