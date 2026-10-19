"""Background worker — keeps the UI responsive during conversion."""

from __future__ import annotations
from pathlib import Path
from PySide6.QtCore import QThread, Signal
from app.core.converter import convert_to_txt

class ConvertWorker(QThread):
    progress = Signal(int)
    log = Signal(str)
    finished_ok = Signal(dict)

    def __init__(self, files: list[Path], parent=None):
        super().__init__(parent)
        self._files = list(files)
        self._cancel = False

    def cancel(self) -> None:
        self._cancel = True

    def run(self) -> None:
        total_files = len(self._files)
        if total_files == 0:
            self.finished_ok.emit({"ok": 0, "failed": [], "total": 0})
            return

        ok = 0
        failed: list[tuple[str, str]] = []

        for i, f in enumerate(self._files, 1):
            if self._cancel:
                break

            self.log.emit(f"⏳ Processing {f.name}...")

            try:
                result = convert_to_txt(f)
                self.log.emit(f"✓ {f.name}  →  {result.name}")
                ok += 1
            except Exception as e:
                self.log.emit(f"✗ {f.name}  →  {e}")
                failed.append((f.name, str(e)))

            self.progress.emit(int(i * 100 / total_files))

        self.finished_ok.emit({"ok": ok, "failed": failed, "total": total_files})
