from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from kvocab_core.document_extractors.base import BaseExtractor, UnsupportedFormatError
from kvocab_core.schemas import ExtractedDocument, ExtractedPage


class HwpExtractor(BaseExtractor):
    extensions = (".hwp",)

    def extract(self, path: Path) -> ExtractedDocument:
        text = self._try_hwp5txt(path) or self._try_prvtext(path)
        if not text:
            raise UnsupportedFormatError(
                "HWP extraction failed. Please save as HWPX or PDF and try again."
            )
        return ExtractedDocument(text=text, pages=[ExtractedPage(page_no=1, text=text)])

    def _try_hwp5txt(self, path: Path) -> str | None:
        exe = shutil.which("hwp5txt")
        if not exe:
            return None
        try:
            proc = subprocess.run(
                [exe, str(path)],
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )
            if proc.returncode == 0 and proc.stdout.strip():
                return proc.stdout
        except Exception:
            return None
        return None

    def _try_prvtext(self, path: Path) -> str | None:
        try:
            import olefile
        except ImportError:
            return None
        if not olefile.isOleFile(str(path)):
            return None
        ole = olefile.OleFileIO(str(path))
        for stream in ("PrvText", "BodyText"):
            if ole.exists(stream):
                data = ole.openstream(stream).read()
                for enc in ("utf-16-le", "cp949", "utf-8"):
                    try:
                        decoded = data.decode(enc, errors="ignore").strip()
                        if decoded:
                            return decoded
                    except Exception:
                        continue
        return None
