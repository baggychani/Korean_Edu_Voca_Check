#!/usr/bin/env python3
"""아이콘 PNG/ICO를 원본 로고에서 다시 만듭니다."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets" / "logo_source.png"
OUT_PNG = ROOT / "src" / "kvocab_desktop" / "assets" / "app_icon.png"
OUT_ICO = ROOT / "src" / "kvocab_desktop" / "assets" / "app_icon.ico"
OUT_SETUP_ICO = ROOT / "src" / "kvocab_desktop" / "assets" / "setup_icon.ico"
CANVAS = 1024
ICO_SIZES = (16, 24, 32, 48, 64, 128, 256)
APP_TARGET_FILL = 0.82
SETUP_TARGET_FILL = 0.96
APP_X_NUDGE = 0.035
APP_Y_NUDGE = -0.015


def _alpha_bbox(image: Image.Image, threshold: int = 8) -> tuple[int, int, int, int] | None:
    alpha = image.getchannel("A")
    mask = alpha.point(lambda value: 255 if value > threshold else 0)
    return mask.getbbox()


def _load_cropped_logo() -> Image.Image:
    if SRC.is_file():
        src = Image.open(SRC).convert("RGBA")
    elif OUT_PNG.is_file():
        src = Image.open(OUT_PNG).convert("RGBA")
    else:
        raise SystemExit("logo_source.png or app_icon.png is required")

    bbox = _alpha_bbox(src)
    if not bbox:
        raise SystemExit("source image has no visible pixels")
    return src.crop(bbox)


def _render_icon(
    cropped: Image.Image,
    *,
    target_fill: float,
    x_nudge: float = 0.0,
    y_nudge: float = 0.0,
) -> Image.Image:
    cw, ch = cropped.size
    scale = (CANVAS * target_fill) / max(cw, ch)
    icon_w = max(1, round(cw * scale))
    icon_h = max(1, round(ch * scale))
    icon = cropped.resize((icon_w, icon_h), Image.Resampling.LANCZOS)

    final = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    x = round((CANVAS - icon_w) / 2 + CANVAS * x_nudge)
    y = round((CANVAS - icon_h) / 2 + CANVAS * y_nudge)
    final.paste(icon, (x, y), icon)
    return final


def _save_ico(image: Image.Image, path: Path) -> None:
    image.save(path, format="ICO", sizes=[(s, s) for s in ICO_SIZES])


def rebuild() -> None:
    cropped = _load_cropped_logo()

    app_icon = _render_icon(
        cropped,
        target_fill=APP_TARGET_FILL,
        x_nudge=APP_X_NUDGE,
        y_nudge=APP_Y_NUDGE,
    )
    app_icon.save(OUT_PNG)
    _save_ico(app_icon, OUT_ICO)

    setup_icon = _render_icon(cropped, target_fill=SETUP_TARGET_FILL)
    _save_ico(setup_icon, OUT_SETUP_ICO)

    print(f"rebuild_icon: wrote {OUT_PNG}, {OUT_ICO}, and {OUT_SETUP_ICO}")


if __name__ == "__main__":
    rebuild()
