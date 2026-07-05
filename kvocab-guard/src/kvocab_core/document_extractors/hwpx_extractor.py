from __future__ import annotations

import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from kvocab_core.document_extractors.base import BaseExtractor
from kvocab_core.schemas import ExtractedDocument, ExtractedPage


class HwpxExtractor(BaseExtractor):
    extensions = (".hwpx",)

    def extract(self, path: Path) -> ExtractedDocument:
        texts: list[str] = []
        with zipfile.ZipFile(path, "r") as zf:
            for name in sorted(zf.namelist()):
                if name.startswith("Contents/section") and name.endswith(".xml"):
                    root = ET.fromstring(zf.read(name))
                    for elem in root.iter():
                        if elem.text and elem.text.strip():
                            texts.append(elem.text.strip())
                        if elem.tail and elem.tail.strip():
                            texts.append(elem.tail.strip())
        text = "\n".join(texts)
        return ExtractedDocument(text=text, pages=[ExtractedPage(page_no=1, text=text)])
