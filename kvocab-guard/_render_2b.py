"""Render selected 2B PDF pages to PNG for visual inspection."""
import sys
from pathlib import Path

import fitz

from kvocab_core.config import TEXTBOOKS_DIR

PATH = TEXTBOOKS_DIR / "서울대 한국어 2B.pdf"
OUT = Path(__file__).resolve().parent / "_2b_pages"
OUT.mkdir(exist_ok=True)

pages = [int(a) for a in sys.argv[1:]]
doc = fitz.open(PATH)
for i in pages:
    if i >= len(doc):
        continue
    pix = doc[i].get_pixmap(dpi=130)
    out = OUT / f"p{i:03d}.png"
    pix.save(out)
    print(out)
doc.close()
