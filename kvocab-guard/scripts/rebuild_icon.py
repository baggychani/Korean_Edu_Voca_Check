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
TARGET_FILL = 0.82
VISUAL_X_NUDGE = 0.035
VISUAL_Y_NUDGE = -0.015


def _alpha_bbox(image: Image.Image, threshold: int = 8) -> tuple[int, int, int, int] | None:
    alpha = image.getchannel("A")
    mask = alpha.point(lambda value: 255 if value > threshold else 0)
    return mask.getbbox()


def rebuild() -> None:
    src = Image.open(SRC).convert("RGBA")
    bbox = _alpha_bbox(src)
    if not bbox:
        raise SystemExit("app_icon.png has no visible pixels")

    cropped = src.crop(bbox)
    cw, ch = cropped.size
    scale = (CANVAS * TARGET_FILL) / max(cw, ch)
    icon_w = max(1, round(cw * scale))
    icon_h = max(1, round(ch * scale))
    icon = cropped.resize((icon_w, icon_h), Image.Resampling.LANCZOS)

    final = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    x = round((CANVAS - icon_w) / 2 + CANVAS * VISUAL_X_NUDGE)
    y = round((CANVAS - icon_h) / 2 + CANVAS * VISUAL_Y_NUDGE)
    final.paste(icon, (x, y), icon)
    final.save(OUT_PNG)

    final.save(
        OUT_ICO,
        format="ICO",
        sizes=[(s, s) for s in ICO_SIZES],
    )
    print(f"rebuild_icon: wrote {OUT_PNG} and {OUT_ICO}")


if __name__ == "__main__":
    rebuild()
