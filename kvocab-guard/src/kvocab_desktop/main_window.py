from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from kvocab_core.allowlist import (
    add_allowlist_item,
    delete_allowlist_item,
    ensure_default_allowlist,
    is_protected_allowlist_norm,
    list_allowlist,
)
from kvocab_core.analyzer import Analyzer, invalidate_lexeme_index
from kvocab_core.config import APP_TITLE, APP_VERSION
from kvocab_core.database import get_counts, init_db
from kvocab_core.dictionary import list_lexemes, search_lexemes_multi
from kvocab_core.models import Lesson, Level, Lexeme
from kvocab_core.schemas import AnalyzeRequest, Strictness
from kvocab_core.seed import full_seed, is_seed_current
from kvocab_core.tools.import_xlsx import import_vocabulary_xlsx
from kvocab_desktop.layout_metrics import (
    ANALYZE_PANEL_MAX_HEIGHT,
    ANALYZE_PANEL_MIN_HEIGHT,
    RESULTS_PANEL_MIN_HEIGHT,
    SIDEBAR_WIDTH,
    WINDOW_DEFAULT_HEIGHT,
    WINDOW_DEFAULT_WIDTH,
    WINDOW_FALLBACK_HEIGHT,
    WINDOW_FALLBACK_MIN_HEIGHT,
    WINDOW_FALLBACK_MIN_WIDTH,
    WINDOW_FALLBACK_WIDTH,
    WINDOW_INITIAL_HEIGHT_RATIO,
    WINDOW_INITIAL_WIDTH_RATIO,
    WINDOW_MIN_HEIGHT,
    WINDOW_MIN_HEIGHT_FLOOR,
    WINDOW_MIN_HEIGHT_RATIO,
    WINDOW_MIN_SCREEN_MARGIN,
    WINDOW_MIN_WIDTH,
    WINDOW_MIN_WIDTH_FLOOR,
    WINDOW_MIN_WIDTH_RATIO,
    WINDOW_SCREEN_MARGIN,
)
from kvocab_desktop.style import APP_STYLESHEET
from kvocab_desktop.widgets.allowlist_panel import AllowlistPanel
from kvocab_desktop.widgets.analyze_panel import AnalyzePanel
from kvocab_desktop.widgets.data_panel import DataPanel
from kvocab_desktop.widgets.dictionary_panel import DictionaryPanel
from kvocab_desktop.widgets.results_panel import ResultsPanel
from kvocab_desktop.widgets.target_selector import TargetSelector


def _initial_window_dimension(default: int, available: int, ratio: float) -> int:
    margin_limited = max(1, available - WINDOW_SCREEN_MARGIN)
    ratio_limited = max(1, int(available * ratio))
    return min(default, margin_limited, ratio_limited)


def _minimum_window_dimension(default: int, floor: int, available: int, ratio: float) -> int:
    margin_limited = max(1, available - WINDOW_MIN_SCREEN_MARGIN)
    ratio_limited = max(1, int(available * ratio))
    return min(default, margin_limited, max(floor, ratio_limited))


class AnalyzeWorker(QThread):
    finished_ok = Signal(object)
    failed = Signal(str)

    def __init__(self, session_factory, request: AnalyzeRequest) -> None:
        super().__init__()
        self.session_factory = session_factory
        self.request = request

    def run(self) -> None:
        try:
            with self.session_factory() as session:
                result = Analyzer(session).analyze(self.request)
            self.finished_ok.emit(result)
        except Exception as exc:
            self.failed.emit(str(exc))


class DbTaskWorker(QThread):
    finished_ok = Signal(object)
    failed = Signal(str)

    def __init__(self, session_factory, task: Callable[[Any], object]) -> None:
        super().__init__()
        self.session_factory = session_factory
        self.task = task

    def run(self) -> None:
        try:
            with self.session_factory() as session:
                result = self.task(session)
            self.finished_ok.emit(result)
        except Exception as exc:
            self.failed.emit(str(exc))


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        screen = QApplication.primaryScreen()
        available = screen.availableGeometry() if screen else None
        if available:
            initial_width = _initial_window_dimension(
                WINDOW_DEFAULT_WIDTH,
                available.width(),
                WINDOW_INITIAL_WIDTH_RATIO,
            )
            initial_height = _initial_window_dimension(
                WINDOW_DEFAULT_HEIGHT,
                available.height(),
                WINDOW_INITIAL_HEIGHT_RATIO,
            )
            min_width = min(
                initial_width,
                _minimum_window_dimension(
                    WINDOW_MIN_WIDTH,
                    WINDOW_MIN_WIDTH_FLOOR,
                    available.width(),
                    WINDOW_MIN_WIDTH_RATIO,
                ),
            )
            min_height = min(
                initial_height,
                _minimum_window_dimension(
                    WINDOW_MIN_HEIGHT,
                    WINDOW_MIN_HEIGHT_FLOOR,
                    available.height(),
                    WINDOW_MIN_HEIGHT_RATIO,
                ),
            )
            self.setMinimumSize(min_width, min_height)
            self.resize(
                initial_width,
                initial_height,
            )
        else:
            self.resize(WINDOW_FALLBACK_WIDTH, WINDOW_FALLBACK_HEIGHT)
            self.setMinimumSize(WINDOW_FALLBACK_MIN_WIDTH, WINDOW_FALLBACK_MIN_HEIGHT)
        self.setStyleSheet(APP_STYLESHEET)

        self.session_factory = init_db()
        self._worker: AnalyzeWorker | None = None
        self._db_worker: DbTaskWorker | None = None

        root = QWidget()
        self.setCentralWidget(root)
        main_layout = QHBoxLayout(root)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        sidebar.setAutoFillBackground(True)
        sidebar.setFixedWidth(SIDEBAR_WIDTH)
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(22, 28, 22, 24)
        sb_layout.setSpacing(0)
        logo_frame = QFrame()
        logo_frame.setObjectName("sidebarLogo")
        logo_lay = QVBoxLayout(logo_frame)
        logo_lay.setContentsMargins(14, 12, 14, 12)
        logo_lay.setSpacing(3)
        tag = QLabel("한국어교육")
        tag.setObjectName("sidebarTag")
        title = QLabel("단어 레벨 검사기")
        title.setObjectName("sidebarTitle")
        subtitle = QLabel("서울대 한국어 교재 기준")
        subtitle.setObjectName("sidebarSubtitle")
        logo_lay.addWidget(tag)
        logo_lay.addWidget(title)
        logo_lay.addWidget(subtitle)
        divider = QFrame()
        divider.setObjectName("sidebarDivider")
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFixedHeight(1)
        sb_layout.addWidget(logo_frame)
        sb_layout.addWidget(divider)
        self.target_selector = TargetSelector()
        sb_layout.addWidget(self.target_selector)
        sb_layout.addStretch()
        version_lbl = QLabel(f"v{APP_VERSION}")
        version_lbl.setObjectName("sidebarVersion")
        copyright_lbl = QLabel("© 2026 Bae Gichan. All rights reserved.")
        copyright_lbl.setObjectName("sidebarCopyright")
        sb_layout.addWidget(version_lbl)
        sb_layout.addWidget(copyright_lbl)
        main_layout.addWidget(sidebar)

        content = QWidget()
        content.setObjectName("contentArea")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(28, 20, 28, 24)
        content_layout.setSpacing(0)
        self.work_status = QLabel("")
        self.work_status.setObjectName("workStatus")
        self.work_status.setVisible(False)
        content_layout.addWidget(self.work_status)
        self.tabs = QTabWidget()
        content_layout.addWidget(self.tabs)
        main_layout.addWidget(content, stretch=1)

        analyze_tab = QWidget()
        analyze_layout = QVBoxLayout(analyze_tab)
        analyze_layout.setContentsMargins(0, 12, 0, 0)
        analyze_layout.setSpacing(0)
        self.analyze_panel = AnalyzePanel()
        self.analyze_panel.setMinimumHeight(ANALYZE_PANEL_MIN_HEIGHT)
        self.analyze_panel.setMaximumHeight(ANALYZE_PANEL_MAX_HEIGHT)
        self.results_panel = ResultsPanel()
        self.results_panel.setMinimumHeight(RESULTS_PANEL_MIN_HEIGHT)
        analyze_layout.addWidget(self.analyze_panel)
        analyze_layout.addSpacing(14)
        analyze_layout.addWidget(self.results_panel, stretch=1)
        self.tabs.addTab(analyze_tab, "검사")

        self.dict_panel = DictionaryPanel()
        self.tabs.addTab(self.dict_panel, "어휘 사전")

        self.allow_panel = AllowlistPanel()
        self.tabs.addTab(self.allow_panel, "허용어")

        self.data_panel = DataPanel()
        self.tabs.addTab(self.data_panel, "데이터")

        self._wire_events()
        self._load_target_data()
        self._ensure_default_characters()
        self._refresh_allowlist()
        self._refresh_counts()
        if not self._ensure_seeded():
            self._load_dictionary_default()

    def _wire_events(self) -> None:
        self.analyze_panel.analyze_requested.connect(self._run_analyze)
        self.analyze_panel.clear_requested.connect(self._on_analyze_clear)
        self.results_panel.sentence_highlight_requested.connect(self.analyze_panel.highlight_issue)
        self.results_panel.issue_selected.connect(self.analyze_panel.highlight_issue)
        self.results_panel.allow_requested.connect(self._add_allow)
        self.results_panel.lemma_lookup_requested.connect(self._lookup_lemma_in_dictionary)
        self.dict_panel.set_search_callback(self._run_dictionary_search)
        self.allow_panel.set_callbacks(None, self._add_allow_item, self._delete_allow_item)
        self.data_panel.set_callbacks(self._run_seed, self._run_import_xlsx)

    def _ensure_default_characters(self) -> None:
        with self.session_factory() as session:
            ensure_default_allowlist(session)

    def _ensure_seeded(self) -> bool:
        with self.session_factory() as session:
            count = session.query(Lexeme).count()
            seed_current = is_seed_current(session) if count else False
        if count == 0 or not seed_current:
            self._run_seed(silent=True)
            return True
        return False

    def _load_target_data(self) -> None:
        with self.session_factory() as session:
            levels = session.query(Level).order_by(Level.sort_order).all()
            lessons = session.query(Lesson).order_by(Lesson.order_index).all()
        by_level: dict[str, list[Lesson]] = {}
        for ls in lessons:
            by_level.setdefault(ls.level, []).append(ls)
        self.target_selector.load_levels(levels, by_level)

    def _target_order_index(self) -> int | None:
        with self.session_factory() as session:
            ls = (
                session.query(Lesson)
                .filter(
                    Lesson.level == self.target_selector.target_level,
                    Lesson.lesson == self.target_selector.target_lesson,
                )
                .one_or_none()
            )
            return ls.order_index if ls else None

    def _build_request(self) -> AnalyzeRequest:
        return AnalyzeRequest(
            text=self.analyze_panel.get_text(),
            target_level=self.target_selector.target_level,
            target_lesson=self.target_selector.target_lesson,
            strictness=Strictness(self.target_selector.strictness),
            use_morph=self.target_selector.use_morph,
            show_debug_ignored=self.target_selector.show_debug,
        )

    def _on_analyze_clear(self) -> None:
        self.analyze_panel.clear_marks()
        self.results_panel.clear()

    def _run_analyze(self) -> None:
        if not self.analyze_panel.get_text().strip():
            QMessageBox.warning(self, "입력 필요", "검사할 텍스트를 입력하세요.")
            return
        self.analyze_panel.clear_marks()
        self.analyze_panel.run_btn.setText("검사 중…")
        self.analyze_panel.run_btn.setEnabled(False)
        self._worker = AnalyzeWorker(self.session_factory, self._build_request())
        self._worker.finished_ok.connect(self._on_analyze_done)
        self._worker.failed.connect(self._on_analyze_fail)
        self._worker.start()

    def _on_analyze_done(self, result) -> None:
        self.analyze_panel.run_btn.setText("텍스트 검사")
        self.analyze_panel.run_btn.setEnabled(True)
        self.results_panel.show_result(result)
        self.analyze_panel.apply_before_introduced_marks(result.issues)

    def _on_analyze_fail(self, msg: str) -> None:
        self.analyze_panel.run_btn.setText("텍스트 검사")
        self.analyze_panel.run_btn.setEnabled(True)
        QMessageBox.critical(self, "검사 오류", msg)

    def _run_dictionary_search(self, query: str) -> None:
        with self.session_factory() as session:
            target_order_index = self._target_order_index()
            if query:
                results = search_lexemes_multi(
                    session,
                    query,
                    target_order_index=target_order_index,
                )
            else:
                results = list_lexemes(
                    session,
                    target_order_index=target_order_index,
                )
        self.dict_panel.show_results(results)

    def _lookup_lemma_in_dictionary(self, lemma: str) -> None:
        lemma = lemma.strip()
        if not lemma:
            return
        self.tabs.setCurrentWidget(self.dict_panel)
        self.dict_panel.search_for(lemma)

    def _load_dictionary_default(self) -> None:
        self._run_dictionary_search("")

    def _add_allow(self, lemma: str, surface: str, first_seen: str = "") -> None:
        text = lemma.strip()
        if not text:
            return

        if surface and surface != text:
            label = f"{surface}({text})"
        else:
            label = text

        target = f"{self.target_selector.target_level} {self.target_selector.target_lesson}"
        detail = ""
        if first_seen:
            detail = f"\n교재상 처음 등장: {first_seen}\n"
        reply = QMessageBox.question(
            self,
            "허용어 목록에 추가",
            f"「{label}」의 원형 「{text}」을(를) 허용어 목록에 추가합니다.{detail}\n"
            f"현재 목표 단원({target})과 관계없이, "
            "앞으로 모든 검사에서 이 원형은 경고하지 않습니다.\n\n"
            "계속하시겠습니까?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        note = f"추가 시 목표: {target}, 표현: {surface or text}"
        if first_seen:
            note += f", 교재 등장: {first_seen}"
        with self.session_factory() as session:
            add_allowlist_item(session, text, note=note)
        self._refresh_allowlist()
        QMessageBox.information(
            self,
            "허용어 목록",
            f"원형 「{text}」을(를) 허용어 목록에 추가했습니다.\n"
            "목표 단원을 바꿔도 이 원형은 경고하지 않습니다.",
        )

    def _add_allow_item(self, text: str, allow_type: str, note: str | None) -> None:
        if not text:
            return
        with self.session_factory() as session:
            add_allowlist_item(session, text, allow_type=allow_type, note=note)
        self._refresh_allowlist()

    def _delete_allow_item(self, item_id: int) -> None:
        with self.session_factory() as session:
            from kvocab_core.models import CustomAllowlist

            item = session.get(CustomAllowlist, item_id)
            if item and is_protected_allowlist_norm(item.normalized_text):
                QMessageBox.information(
                    self,
                    "허용어 삭제",
                    "교재 고정 등장인물은 삭제할 수 없습니다.",
                )
                return
            if not delete_allowlist_item(session, item_id):
                return
        self._refresh_allowlist()

    def _refresh_allowlist(self) -> None:
        with self.session_factory() as session:
            items = list_allowlist(session)
        from kvocab_core.schemas import AllowlistItem

        self.allow_panel.show_items(
            [
                AllowlistItem(
                    id=i.id,
                    text=i.text,
                    normalized_text=i.normalized_text,
                    allow_type=i.allow_type,
                    note=i.note,
                    is_protected=is_protected_allowlist_norm(i.normalized_text),
                )
                for i in items
            ]
        )

    def _refresh_counts(self) -> None:
        with self.session_factory() as session:
            self.data_panel.show_counts(get_counts(session))

    def _start_db_task(
        self,
        task: Callable[[Any], object],
        *,
        busy_message: str,
        error_title: str,
        on_success: Callable[[object], None],
    ) -> None:
        if self._db_worker is not None and self._db_worker.isRunning():
            QMessageBox.information(self, "작업 진행 중", "DB 작업이 이미 진행 중입니다.")
            return
        worker = DbTaskWorker(self.session_factory, task)
        self._db_worker = worker
        worker.finished_ok.connect(lambda result: self._on_db_task_done(result, on_success))
        worker.failed.connect(lambda msg: self._on_db_task_failed(msg, error_title))
        worker.finished.connect(lambda: self._release_db_worker(worker))
        self._set_db_busy(True, busy_message)
        worker.start()

    def _on_db_task_done(self, result, on_success: Callable[[object], None]) -> None:
        self._set_db_busy(False)
        on_success(result)

    def _on_db_task_failed(self, msg: str, title: str) -> None:
        self._set_db_busy(False)
        QMessageBox.critical(self, title, msg)

    def _release_db_worker(self, worker: DbTaskWorker) -> None:
        if self._db_worker is worker:
            self._db_worker = None
        worker.deleteLater()

    def _set_db_busy(self, busy: bool, message: str = "") -> None:
        self.work_status.setText(message)
        self.work_status.setVisible(busy and bool(message))
        self.data_panel.set_busy(busy, message)

    def _run_seed(self, silent: bool = False) -> None:
        if not silent:
            reply = QMessageBox.warning(
                self,
                "DB 초기화",
                "DB를 초기화하고 seed를 다시 불러옵니다.\n"
                "어휘 데이터는 새로 불러오고, 사용자가 추가한 허용어는 보존됩니다.\n\n"
                "정말 계속하시겠습니까?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        def on_success(stats: object) -> None:
            invalidate_lexeme_index()
            self._load_target_data()
            self._refresh_counts()
            self._refresh_allowlist()
            self._load_dictionary_default()
            if not silent:
                QMessageBox.information(
                    self, "Seed 완료", f"DB를 초기화하고 seed를 불러왔습니다.\n{stats}"
                )

        self._start_db_task(
            lambda session: full_seed(session, preserve_allowlist=True),
            busy_message="DB를 초기화하고 seed를 불러오는 중입니다.",
            error_title="Seed 오류",
            on_success=on_success,
        )

    def _run_import_xlsx(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "XLSX 가져오기", "", "Excel (*.xlsx);;All (*.*)"
        )
        if not path:
            return
        def on_success(stats: object) -> None:
            invalidate_lexeme_index()
            self._refresh_counts()
            QMessageBox.information(self, "가져오기 완료", str(stats))

        xlsx_path = Path(path)
        self._start_db_task(
            lambda session: import_vocabulary_xlsx(session, xlsx_path),
            busy_message="XLSX를 가져오는 중입니다.",
            error_title="가져오기 오류",
            on_success=on_success,
        )
