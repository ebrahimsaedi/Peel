"""Drag & drop zone for all supported formats."""

from __future__ import annotations
from pathlib import Path
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFileDialog, QFrame, QLabel, QVBoxLayout

ALLOWED_EXTS = {
    ".epub", ".mobi", ".azw3", ".fb2", ".pdf", ".docx", ".odt", ".rtf",
    ".txt", ".md", ".html", ".htm", ".xhtml", ".csv", ".json", ".tex",
    ".pptx", ".srt", ".vtt", ".ass", ".ssa", ".xlsx", ".xls", ".ods",
    ".yaml", ".yml", ".xml", ".tsv", ".ipynb", ".eml"
}

class DropArea(QFrame):
    filesDropped = Signal(list)
    rejected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dropArea")
        self.setAcceptDrops(True)
        self.setMinimumHeight(140)
        self.setProperty("dragging", "false")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        self._hint = QLabel("Drag & drop your documents here\nor click to browse")
        self._hint.setObjectName("dropHint")
        self._hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._hint)

    def dragEnterEvent(self, event):
        urls = event.mimeData().urls() if event.mimeData().hasUrls() else []
        if any(u.toLocalFile().lower().endswith(tuple(ALLOWED_EXTS)) for u in urls):
            event.acceptProposedAction()
            self._set_dragging(True)
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self._set_dragging(False)
        super().dragLeaveEvent(event)

    def dropEvent(self, event):
        self._set_dragging(False)
        paths: list[Path] = []
        for url in event.mimeData().urls():
            local = url.toLocalFile()
            if not local: continue
            p = Path(local)
            if p.is_file() and p.suffix.lower() in ALLOWED_EXTS:
                paths.append(p)

        if paths:
            event.acceptProposedAction()
            self.filesDropped.emit(paths)
        else:
            event.ignore()
            self.rejected.emit("Unsupported file format.")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            files, _ = QFileDialog.getOpenFileNames(
                self,
                "Choose files",
                "",
                "All Supported (*.*);;All files (*)",
            )
            if files:
                self.filesDropped.emit([Path(f) for f in files])
        super().mousePressEvent(event)

    def _set_dragging(self, active: bool):
        self.setProperty("dragging", "true" if active else "false")
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
