#!/usr/bin/env python3
"""Builds the two aspect ratios of the LUFT Seoul ad from src/template.html.

  python3 build.py            -> index.html (9:16) + landscape.html (16:9), look A
  python3 build.py --look b   -> same files in look B (peach mono) for look tests

Everything is laid out inside a 1080x1080 "core" that is centred horizontally;
in 9:16 the core sits high (top 240) so all words stay inside the 168-1330 px band.
"""
import math, sys, pathlib

ROOT = pathlib.Path(__file__).parent
DUR = 20.0
LOOKS = {
    "a": dict(GROUND="#120E0B", GROUND2="#2A1C12", INK="#FBF6F1", INK2="rgba(251,246,241,.62)", GLOW="#FFB066", VIG=".55", GRAIN=".07"),
    "b": dict(GROUND="#F1C7A6", GROUND2="#F6D8C0", INK="#141210", INK2="#4A433D", GLOW="#141210", VIG="0", GRAIN=".05"),
}
LAND_CSS = """
#s4-case{left:290px;top:10px;width:500px;height:868px}
#s4-cap{top:900px}
#s5-card{left:-330px;top:60px;width:600px}
#s7-in{transform:scale(.9);transform-origin:540px 470px}
"""
LOOK_B_CSS = """
#s1-sym{filter:none}
#s2-phone{box-shadow:0 0 0 2px #2b2521,0 50px 90px rgba(90,50,20,.35)}
#s2-steps .st{border-color:rgba(20,18,16,.25);color:rgba(20,18,16,.5)}
#s3-head h2,#s6-a,#s6-b,#s4-cap b,#s5-card b{color:#141210}
#s3-head .mono,#s4-cap .mono{color:#B4441F}
"""

def build(fmt, look):
    if fmt == "portrait":
        W, H, OX, OY, res, out = 1080, 1920, 0, 240, "portrait", "index.html"
        SP_L, SP_R = 30, 700
        PS = 1.1
    else:
        W, H, OX, OY, res, out = 1920, 1080, 420, 0, "landscape", "../luft-seoul-16x9/index.html"
        SP_L, SP_R = -60, 790
        PS = 1.0
    tokens = dict(
        W=W, H=H, OX=OX, OY=OY, RES=res, DUR=DUR, S7DUR=round(DUR - 17.15, 2),
        LAND=1 if fmt == "landscape" else 0, LOOK=look,
        GLOWY=round((OY + 480) / H * 100, 1),
        IRISY=OY + 640, IRISR=int(math.hypot(W, H)) + 40,
        SP_L=SP_L, SP_R=SP_R, PHONE_SCALE=PS, MAPCARD_Y=840 if fmt == "portrait" else 40,
        RING_S=1.22 if fmt == "portrait" else 1.0, RING_Y=560 if fmt == "portrait" else 520, NAMES_Y=960 if fmt == "portrait" else 880,
        EXTRA_CSS=(LOOK_B_CSS if look == "b" else "") + (LAND_CSS if fmt == "landscape" else ""),
        **LOOKS[look],
    )
    html = (ROOT / "src/template.html").read_text()
    for k, v in tokens.items():
        html = html.replace("{{" + k + "}}", str(v))
    assert "{{" not in html, html[html.index("{{"):html.index("{{") + 40]
    (ROOT / out).parent.mkdir(exist_ok=True)
    (ROOT / out).write_text(html)
    print("wrote", out, W, "x", H, "look", look)

if __name__ == "__main__":
    look = sys.argv[sys.argv.index("--look") + 1] if "--look" in sys.argv else "a"
    for fmt in ("portrait", "landscape"):
        build(fmt, look)
