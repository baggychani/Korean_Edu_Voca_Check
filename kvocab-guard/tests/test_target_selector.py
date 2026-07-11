from __future__ import annotations

import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from kvocab_core.models import Lesson, Level
from kvocab_desktop.widgets.target_selector import TargetSelector


def _app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv[:1])
    return app


def _lesson(level: str, lesson: str, order_index: int) -> Lesson:
    return Lesson(
        level=level,
        lesson=lesson,
        unit_no=1,
        lesson_no=int(lesson.split("-")[1]),
        unit_topic="인사",
        unit_title="인사",
        page_start=1,
        page_end=10,
        order_index=order_index,
    )


def test_load_levels_restores_saved_level_and_lesson() -> None:
    _app()
    selector = TargetSelector()
    levels = [
        Level(
            level="1A",
            series="서울대 한국어",
            title_ko="서울대 한국어 1A",
            title_en="SNU Korean 1A",
            level_order=101,
            sort_order=1,
        ),
        Level(
            level="1B",
            series="서울대 한국어",
            title_ko="서울대 한국어 1B",
            title_en="SNU Korean 1B",
            level_order=102,
            sort_order=2,
        ),
    ]
    lessons = {
        "1A": [_lesson("1A", "1-1", 101011)],
        "1B": [_lesson("1B", "1-1", 102011), _lesson("1B", "1-2", 102012)],
    }

    selector.load_levels(
        levels,
        lessons,
        selected_level="1B",
        selected_lesson="1-2",
    )

    assert selector.target_level == "1B"
    assert selector.target_lesson == "1-2"
