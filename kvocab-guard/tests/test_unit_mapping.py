from __future__ import annotations

import pytest

from kvocab_core.config import compute_order_index
from kvocab_core.database import init_db
from kvocab_core.models import Lesson
from kvocab_core.seed import seed_levels_and_lessons
from kvocab_core.tools.import_xlsx import lesson_for_page


@pytest.fixture
def seeded_session(tmp_path):
    factory = init_db(tmp_path / "test.db")
    with factory() as session:
        seed_levels_and_lessons(session, "2A")
        lessons = (
            session.query(Lesson).filter(Lesson.level == "2A").order_by(Lesson.order_index).all()
        )
        yield session, lessons


@pytest.mark.parametrize(
    "page,expected_lesson",
    [
        (22, "1-1"),
        (28, "1-2"),
        (38, "2-1"),
        (44, "2-2"),
        (156, "9-2"),
        (62, "3-2"),
        (107, "6-1"),
        (140, "8-2"),
    ],
)
def test_page_to_lesson(seeded_session, page, expected_lesson):
    session, lessons = seeded_session
    found = lesson_for_page(lessons, page)
    assert found is not None
    assert found.lesson == expected_lesson


def test_order_index_2a_2_2():
    assert compute_order_index("2A", 2, 2) == 201022


def test_order_index_cross_level():
    assert compute_order_index("1B", 1, 1) == 102011
    assert compute_order_index("2A", 1, 1) == 201011
    assert compute_order_index("1A", 9, 2) == 101092
    assert compute_order_index("1B", 1, 1) < compute_order_index("2A", 1, 1)
