"""Main window for Peel."""

from __future__ import annotations
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QMainWindow, QMessageBox, QPlainTextEdit, QProgressBar,
    QPushButton, QVBoxLayout, QWidget,
)

from app.ui import theme
from app.ui.drop_area import DropArea
from app.ui.worker import ConvertWorker

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Peel")
        self.resize(520, 720)

        self._files: list[Path] = []
        self._worker: ConvertWorker | None = None

        self._build_ui()
        self._apply_theme()

    def _build_ui(self) -> None:
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(14)

        title = QLabel("Peel")
        title.setObjectName("title")
        root.addWidget(title)

        subtitle = QLabel("Extract clean text from documents and ebooks.")
        subtitle.setObjectName("dropHint")
        root.addWidget(subtitle)

        self.drop_area = DropArea()
        self.drop_area.filesDropped.connect(self._add_files)
        self.drop_area.rejected.connect(self._on_rejected)
        root.addWidget(self.drop_area)

        root.addWidget(QLabel("Files"))
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.ExtendedSelection)
        self.file_list.setMaximumHeight(100)
        root.addWidget(self.file_list)

        row_btns = QHBoxLayout()
        add_btn = QPushButton("Add files…")
        add_btn.setObjectName("ghost")
        add_btn.clicked.connect(self._browse)
        remove_btn = QPushButton("Remove selected")
        remove_btn.setObjectName("ghost")
        remove_btn.clicked.connect(self._remove_selected)
        clear_btn = QPushButton("Clear")
        clear_btn.setObjectName("ghost")
        clear_btn.clicked.connect(self._clear_files)
        row_btns.addWidget(add_btn)
        row_btns.addWidget(remove_btn)
        row_btns.addStretch()
        row_btns.addWidget(clear_btn)
        root.addLayout(row_btns)

        self.convert_btn = QPushButton("Convert to TXT")
        self.convert_btn.setMinimumHeight(44)
        self.convert_btn.clicked.connect(self._start_convert)
        root.addWidget(self.convert_btn)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        root.addWidget(self.progress)

        root.addWidget(QLabel("Conversion Log"))
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setMinimumHeight(120)
        root.addWidget(self.log)

    def _apply_theme(self) -> None:
        self.setStyleSheet(theme.stylesheet())

    def _add_files(self, paths: list[Path]) -> None:
        existing = {str(p) for p in self._files}
        added = 0
        for p in paths:
            if str(p) in existing:
                continue
            self._files.append(p)
            item = QListWidgetItem(p.name)
            item.setToolTip(str(p))
            item.setData(Qt.UserRole, str(p))
            self.file_list.addItem(item)
            added += 1
        if added:
            self._log(f"Added {added} file(s). Total: {len(self._files)}.")

    def _on_rejected(self, reason: str) -> None:
        QMessageBox.warning(self, "Peel", reason)

    def _browse(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self, "Choose files", "", "All Supported (*.*);;All files (*)"
        )
        if files:
            self._add_files([Path(f) for f in files])

    def _remove_selected(self) -> None:
        for item in self.file_list.selectedItems():
            path = Path(item.data(Qt.UserRole))
            self._files = [p for p in self._files if p != path]
            self.file_list.takeItem(self.file_list.row(item))

    def _clear_files(self) -> None:
        self._files.clear()
        self.file_list.clear()

    def _start_convert(self) -> None:
        if self._worker and self._worker.isRunning():
            return
        if not self._files:
            QMessageBox.information(self, "Peel", "Add at least one file first.")
            return

        self.log.clear()
        self.progress.setValue(0)
        self._set_busy(True)

        self._log(f"Converting {len(self._files)} file(s)…")

        self._worker = ConvertWorker(self._files, parent=self)
        self._worker.progress.connect(self.progress.setValue)
        self._worker.log.connect(self._log)
        self._worker.finished_ok.connect(self._on_finished)
        self._worker.finished.connect(lambda: self._set_busy(False))
        self._worker.start()

    def _on_finished(self, summary: dict) -> None:
        ok = summary["ok"]
        failed = summary["failed"]
        total = summary["total"]
        self._log(f"Done. {ok}/{total} succeeded.")
        if failed:
            self._log(f"{len(failed)} file(s) failed.")
        else:
            QMessageBox.information(self, "Peel", f"All done! {ok} file(s) converted.")

    def _set_busy(self, busy: bool) -> None:
        self.convert_btn.setEnabled(not busy)
        self.convert_btn.setText("Converting…" if busy else "Convert to TXT")
        self.drop_area.setEnabled(not busy)

    def _log(self, msg: str) -> None:
        self.log.appendPlainText(msg)
