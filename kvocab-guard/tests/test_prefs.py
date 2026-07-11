from __future__ import annotations

import json

from kvocab_desktop import prefs


def test_prefs_round_trip_target_selection(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(prefs, "app_data_dir", lambda: tmp_path)
    expected = {
        "last_update_check": "2026-07-11T12:00:00",
        "last_target_level": "1A",
        "last_target_lesson": "1-1",
    }

    prefs.save_prefs(expected)

    assert prefs.load_prefs() == expected


def test_load_prefs_rejects_non_object_json(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(prefs, "app_data_dir", lambda: tmp_path)
    (tmp_path / "prefs.json").write_text(json.dumps(["not", "an", "object"]), encoding="utf-8")

    assert prefs.load_prefs() == {}
