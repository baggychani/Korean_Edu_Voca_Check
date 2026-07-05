from __future__ import annotations

from pathlib import Path

from kvocab_core.document_extractors.base import BaseExtractor, UnsupportedFormatError
from kvocab_core.document_extractors.docx_extractor import DocxExtractor
from kvocab_core.document_extractors.hwp_extractor import HwpExtractor
from kvocab_core.document_extractors.hwpx_extractor import HwpxExtractor
from kvocab_core.document_extractors.pdf_extractor import PdfExtractor
from kvocab_core.document_extractors.txt_extractor import TxtExtractor
from kvocab_core.schemas import ExtractedDocument

_EXTRACTORS: list[BaseExtractor] = [
    TxtExtractor(),
    PdfExtractor(),
    HwpxExtractor(),
    HwpExtractor(),
    DocxExtractor(),
]


def extract_document(path: Path) -> ExtractedDocument:
    path = Path(path)
    suffix = path.suffix.lower()
    for ext in _EXTRACTORS:
        if suffix in ext.extensions:
            return ext.extract(path)
    raise UnsupportedFormatError(f"Unsupported file type: {suffix}")
