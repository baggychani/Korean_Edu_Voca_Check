from __future__ import annotations

from pathlib import Path

import fitz

from kvocab_core.document_extractors.base import BaseExtractor
from kvocab_core.schemas import ExtractedDocument, ExtractedPage


class PdfExtractor(BaseExtractor):
    extensions = (".pdf",)

    def extract(self, path: Path) -> ExtractedDocument:
        pages: list[ExtractedPage] = []
        with fitz.open(path) as doc:
            for i, page in enumerate(doc, start=1):
                pages.append(ExtractedPage(page_no=i, text=page.get_text()))
        text = "\n".join(p.text for p in pages)
        non_ws = sum(1 for ch in text if not ch.isspace())
        if non_ws < 20:
            return ExtractedDocument(
                text="",
                pages=pages,
                message="PDF에서 텍스트를 거의 추출하지 못했습니다. 이미지 PDF일 수 있으므로 OCR이 필요합니다.",
            )
        return ExtractedDocument(text=text, pages=pages)
