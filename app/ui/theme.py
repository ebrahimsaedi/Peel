"""
Theme detection + QSS for Chop.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication


def is_dark() -> bool:
    """True if the OS reports a dark color scheme."""
    hints = QGuiApplication.styleHints()
    try:
        scheme = hints.colorScheme()
        return scheme == Qt.ColorScheme.Dark
    except AttributeError:
        return False


def stylesheet() -> str:
    return _DARK_QSS if is_dark() else _LIGHT_QSS


# ---------------------------------------------------------------------------
# Stylesheets
# ---------------------------------------------------------------------------

_LIGHT_QSS = """
QMainWindow, QWidget#centralWidget {
    background: #f7f7f9;
}
QWidget {
    color: #1f2328;
    font-size: 13px;
}
QLabel#title {
    font-size: 22px;
    font-weight: 700;
    color: #111827;
}
QFrame#dropArea {
    background: #ffffff;
    border: 2px dashed #c7c9cf;
    border-radius: 12px;
}
QFrame#dropArea[dragging="true"] {
    border-color: #3b82f6;
    background: #eff6ff;
}
QLabel#dropHint {
    color: #4b5563;
    font-size: 14px;
}
QPushButton {
    background: #3b82f6;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 8px 18px;
    font-weight: 600;
}
QPushButton:hover  { background: #2563eb; }
QPushButton:pressed{ background: #1d4ed8; }
QPushButton:disabled{ background: #c7c9cf; color: #6b7280; }
QPushButton#ghost {
    background: transparent;
    color: #6b7280;
    font-weight: normal;
    padding: 4px 8px;
}
QPushButton#ghost:hover { color: #1f2328; }

/* --- Custom SpinBox and Step Buttons --- */
QSpinBox {
    background: #ffffff;
    border: 1px solid #d0d3d9;
    border-radius: 8px;
    padding: 6px 8px;
    color: #1f2328;
    font-weight: 600;
}
QPushButton#stepBtn {
    background: #e5e7eb;
    color: #374151;
    border-radius: 16px; /* دایره‌ای کردن */
    font-size: 18px;
    font-weight: bold;
    padding: 0;
    border: none;
}
QPushButton#stepBtn:hover {
    background: #d1d5db;
}
QPushButton#stepBtn:pressed {
    background: #9ca3af;
}

QListWidget {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 4px;
    min-height: 80px;
}
QListWidget::item {
    padding: 4px;
    border-bottom: 1px solid #f3f4f6;
}

QProgressBar {
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    background: #ffffff;
    text-align: center;
    height: 18px;
    color: #1f2328;
    font-weight: bold;
}
QProgressBar::chunk {
    background: #3b82f6;
    border-radius: 6px;
}
QPlainTextEdit {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    font-family: monospace;
    font-size: 12px;
    color: #1f2328;
}
"""

_DARK_QSS = """
QMainWindow, QWidget#centralWidget {
    background: #1e1f22;
}
QWidget {
    color: #e6e6e6;
    font-size: 13px;
}
QLabel#title {
    font-size: 22px;
    font-weight: 700;
    color: #ffffff;
}
QFrame#dropArea {
    background: #2a2b2f;
    border: 2px dashed #4a4c53;
    border-radius: 12px;
}
QFrame#dropArea[dragging="true"] {
    border-color: #60a5fa;
    background: #1e293b;
}
QLabel#dropHint {
    color: #9ca3af;
    font-size: 14px;
}
QPushButton {
    background: #3b82f6;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 8px 18px;
    font-weight: 600;
}
QPushButton:hover  { background: #2563eb; }
QPushButton:pressed{ background: #1d4ed8; }
QPushButton:disabled{ background: #3a3b40; color: #6b7280; }
QPushButton#ghost {
    background: transparent;
    color: #9ca3af;
    font-weight: normal;
    padding: 4px 8px;
}
QPushButton#ghost:hover { color: #e6e6e6; }

/* --- Custom SpinBox and Step Buttons --- */
QSpinBox {
    background: #2a2b2f;
    border: 1px solid #4a4c53;
    border-radius: 8px;
    padding: 6px 8px;
    color: #e6e6e6;
    font-weight: 600;
}
QPushButton#stepBtn {
    background: #3a3b40;
    color: #e5e7eb;
    border-radius: 16px;
    font-size: 18px;
    font-weight: bold;
    padding: 0;
    border: none;
}
QPushButton#stepBtn:hover {
    background: #4a4c53;
}
QPushButton#stepBtn:pressed {
    background: #6b7280;
}

QListWidget {
    background: #2a2b2f;
    border: 1px solid #3a3b40;
    border-radius: 8px;
    padding: 4px;
    min-height: 80px;
}
QListWidget::item {
    padding: 4px;
    border-bottom: 1px solid #3a3b40;
}

QProgressBar {
    border: 1px solid #3a3b40;
    border-radius: 6px;
    background: #2a2b2f;
    text-align: center;
    height: 18px;
    color: #e6e6e6;
    font-weight: bold;
}
QProgressBar::chunk {
    background: #3b82f6;
    border-radius: 6px;
}
QPlainTextEdit {
    background: #2a2b2f;
    border: 1px solid #3a3b40;
    border-radius: 8px;
    font-family: monospace;
    font-size: 12px;
    color: #d1d5db;
}
"""
