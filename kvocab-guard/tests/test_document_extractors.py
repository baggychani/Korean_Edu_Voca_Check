from __future__ import annotations

import pytest

from kvocab_core.document_extractors import extract_document


def test_txt_extractor(tmp_path):
    p = tmp_path / "sample.txt"
    p.write_text("안녕하세요", encoding="utf-8")
    doc = extract_document(p)
    assert "안녕" in doc.text


def test_unsupported_format(tmp_path):
    p = tmp_path / "file.xyz"
    p.write_text("x", encoding="utf-8")
    from kvocab_core.document_extractors.base import UnsupportedFormatError

    with pytest.raises(UnsupportedFormatError):
        extract_document(p)
