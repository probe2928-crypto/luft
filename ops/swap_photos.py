"""실물 촬영본을 사이트 이미지 경로로 교체한다. (ops/SAMPLE_WEEK.md ③ 참고)

사용:
  python3 ops/swap_photos.py moonjar          # S01~S06 케이스 컷
  python3 ops/swap_photos.py --scent celadon  # S07·S09·S10 방향제 컷 (S08은 공통)
촬영본은 ops/incoming/ 에 SAMPLE_WEEK.md 의 파일명대로 둔다.
"""
import sys
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
INC = ROOT / "ops" / "incoming"
CASES = {"ilwol", "moonjar", "celadon", "najeon", "peony", "bojagi", "dancheong"}
SCENTS = {"moonjar", "celadon", "pyeonbaek"}


def fit(src: Path, dst: Path, size):
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    im = ImageOps.fit(im, size, Image.LANCZOS, centering=(0.5, 0.5))
    dst.parent.mkdir(parents=True, exist_ok=True)
    im.save(dst, quality=88, optimize=True, progressive=True)
    print(f"{src.name} -> {dst.relative_to(ROOT)} {size[0]}x{size[1]}")


def run(pairs):
    done = 0
    for name, dst, size in pairs:
        src = INC / name
        if src.exists():
            fit(src, ROOT / dst, size)
            done += 1
        else:
            print(f"(없음) {name}")
    print(f"교체 {done}건. 다음: smartstore/detail.html 다시 찍어 detail-860.png 갱신")


def main(argv):
    if len(argv) >= 2 and argv[0] == "--scent":
        k = argv[1]
        assert k in SCENTS, f"향 이름은 {sorted(SCENTS)} 중 하나"
        run([
            ("S07_scent_front.jpg", f"img/v2/scent-{k}.jpg", (1000, 1000)),
            ("S08_scent_lineup.jpg", "img/v2/scent-lineup.jpg", (1600, 1000)),
            ("S09_scent_cupholder.jpg", f"img/v2/scent-cupholder-{k}.jpg", (1000, 1000)),
            ("S10_scent_open.jpg", "img/v2/scent-open.jpg", (1000, 1000)),
        ])
    elif len(argv) == 1:
        k = argv[0]
        assert k in CASES, f"케이스 이름은 {sorted(CASES)} 중 하나"
        run([
            ("S01_case_front.jpg", f"img/v2/{k}-front.jpg", (1000, 1000)),
            ("S02_case_angle.jpg", f"img/v2/{k}-main.jpg", (1000, 1000)),
            ("S03_case_hand.jpg", f"img/v2/{k}-hand.jpg", (1000, 1000)),
            ("S04_case_flat.jpg", f"img/v2/{k}-flat.jpg", (1000, 1000)),
            ("S05_case_detail.jpg", f"img/v2/{k}-edge.jpg", (1000, 1000)),
            ("S06_case_lineup.jpg", "img/v2/seoul-lineup.jpg", (1600, 1000)),
        ])
    else:
        print(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
