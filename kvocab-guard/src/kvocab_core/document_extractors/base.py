from __future__ import annotations

from pathlib import Path

from kvocab_core.schemas import ExtractedDocument


class UnsupportedFormatError(Exception):
    pass


class BaseExtractor:
    extensions: tuple[str, ...] = ()

    def extract(self, path: Path) -> ExtractedDocument:
        raise NotImplementedError
