from __future__ import annotations

from pathlib import Path

from kvocab_core.document_extractors.base import BaseExtractor
from kvocab_core.schemas import ExtractedDocument, ExtractedPage


class TxtExtractor(BaseExtractor):
    extensions = (".txt",)

    def extract(self, path: Path) -> ExtractedDocument:
        text = path.read_text(encoding="utf-8", errors="replace")
        return ExtractedDocument(text=text, pages=[ExtractedPage(page_no=1, text=text)])
