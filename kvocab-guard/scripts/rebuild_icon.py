#!/usr/bin/env python3
"""아이콘 PNG/ICO를 원본 로고에서 다시 만듭니다."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets" / "logo_source.png"
OUT_PNG = ROOT / "src" / "kvocab_desktop" / "assets" / "app_icon.png"
OUT_ICO = ROOT / "src" / "kvocab_desktop" / "assets" / "app_icon.ico"
CANVAS = 1024
ICO_SIZES = (16, 24, 32, 48, 64, 128, 256)


def rebuild() -> None:
    src = Image.open(SRC).convert("RGBA")
    bbox = src.getbbox()
    if not bbox:
        raise SystemExit("app_icon.png has no visible pixels")

    cropped = src.crop(bbox)
    cw, ch = cropped.size
    side = max(cw, ch)
    margin = max(16, int(side * 0.06))
    square = side + margin * 2
    canvas = Image.new("RGBA", (square, square), (0, 0, 0, 0))
    x = (square - cw) // 2
    y = (square - ch) // 2
    canvas.paste(cropped, (x, y), cropped)

    final = canvas.resize((CANVAS, CANVAS), Image.Resampling.LANCZOS)
    final.save(OUT_PNG)

    final.save(
        OUT_ICO,
        format="ICO",
        sizes=[(s, s) for s in ICO_SIZES],
    )
    print(f"rebuild_icon: wrote {OUT_PNG} and {OUT_ICO}")


if __name__ == "__main__":
    rebuild()
