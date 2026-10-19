"""Core conversion logic for Peel — V1 (No OCR)."""

from __future__ import annotations
import subprocess
import shutil
import json
import csv
import re
import email
import os
import sys
import tempfile
from email import policy
from pathlib import Path
from bs4 import BeautifulSoup
import pypandoc
from pypdf import PdfReader

class ConvertError(Exception):
    pass

def convert_to_txt(source: str | Path, out_dir: str | Path | None = None) -> Path:
    src = Path(source).resolve()
    if not src.exists():
        raise FileNotFoundError(f"File not found: {src}")

    ext = src.suffix.lower()
    out = Path(out_dir).resolve() if out_dir is not None else src.parent
    out.mkdir(parents=True, exist_ok=True)
    dst = out / f"{src.stem}.txt"

    if ext == ".txt":
        shutil.copy2(src, dst)
        return dst

    try:
        if ext in (".epub", ".mobi", ".azw3", ".fb2", ".lit", ".prc", ".pdb"):
            _run_calibre(src, dst)

        elif ext == ".pdf":
            _run_pypdf(src, dst)

        elif ext in (".docx", ".doc", ".odt", ".rtf", ".md", ".html", ".htm", ".xhtml",
                     ".tex", ".pptx", ".xlsx", ".xls", ".ods", ".csv", ".tsv", ".yaml", ".yml"):
            _run_pypandoc(src, dst)

        elif ext in (".json", ".srt", ".vtt", ".ass", ".ssa", ".ipynb", ".eml", ".xml"):
            _run_python_extractor(src, dst, ext)

        else:
            raise ConvertError(f"Unsupported format: {ext}")
    except Exception as e:
        raise ConvertError(f"Failed to parse {src.name}: {e}") from e

    if not dst.exists() or dst.stat().st_size == 0:
        raise ConvertError("Conversion failed: The output file is empty.")

    return dst

# ---------------------------------------------------------
# Native PDF & Pandoc Runners
# ---------------------------------------------------------
def _run_pypdf(src: Path, dst: Path) -> None:
    reader = PdfReader(str(src))
    parts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            parts.append(text)
    dst.write_text("\n\n".join(parts), encoding="utf-8")

def _run_pypandoc(src: Path, dst: Path) -> None:
    try:
        output = pypandoc.convert_file(str(src), 'plain')
        dst.write_text(output, encoding="utf-8")
    except Exception as e:
        raise ConvertError(f"Pandoc conversion failed: {e}")

# ---------------------------------------------------------
# External Tools (Calibre Only)
# ---------------------------------------------------------
def _get_vendor_calibre() -> Path | None:
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).resolve().parents[2]
    portable_calibre = base / "vendor" / "calibre" / "calibre" / "ebook-convert"
    if not portable_calibre.exists():
        portable_calibre = base / "vendor" / "calibre" / "ebook-convert"
    return portable_calibre if portable_calibre.exists() else None

def _run_calibre(src: Path, dst: Path) -> None:
    portable_calibre = _get_vendor_calibre()
    if not portable_calibre and not shutil.which("ebook-convert"):
        raise ConvertError("Calibre not found. Please install it or place it in the 'vendor' folder.")

    cmd_bin = str(portable_calibre) if portable_calibre else "ebook-convert"
    cmd = [cmd_bin, str(src), str(dst)]

    env = os.environ.copy()

    # --- این ۴ خط راز اصلی حل مشکل هستن ---
    # ما همه مسیرهای کتابخانه‌های برنامه خودمون رو پاک می‌کنیم تا Calibre مجبور بشه از کتابخانه‌های خودش استفاده کنه
    env.pop("PYTHONHOME", None)
    env.pop("PYTHONPATH", None)
    env.pop("LD_LIBRARY_PATH", None)
    env.pop("QT_PLUGIN_PATH", None)
    # ----------------------------------------

    env["QT_QPA_PLATFORM"] = "offscreen"

    temp_config = os.path.join(tempfile.gettempdir(), "peel_calibre_config")
    os.makedirs(temp_config, exist_ok=True)
    env["CALIBRE_CONFIG_DIRECTORY"] = temp_config

    _exec_subprocess(cmd, env=env)

def _exec_subprocess(cmd: list[str], env: dict | None = None) -> None:
    try:
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env
        )
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            error_msg = stderr.strip() if stderr else "Unknown error"
            raise ConvertError(f"Tool failed: {error_msg}")
    except Exception as e:
        raise ConvertError(f"Execution error: {e}")

# ---------------------------------------------------------
# Python Extractors
# ---------------------------------------------------------
def _run_python_extractor(src: Path, dst: Path, ext: str) -> None:
    text = ""
    if ext == ".json":
        data = json.loads(src.read_text(encoding="utf-8", errors="ignore"))
        text = json.dumps(data, indent=2, ensure_ascii=False)
    elif ext in (".srt", ".vtt", ".ass", ".ssa"):
        raw = src.read_text(encoding="utf-8", errors="ignore")
        raw = re.sub(r'\d{2}:\d{2}:\d{2}[,.]\d{3} --> \d{2}:\d{2}:\d{2}[,.]\d{3}', '', raw)
        raw = re.sub(r'\{.*?\}', '', raw)
        raw = re.sub(r'<[^>]+>', '', raw)
        text = "\n".join(line.strip() for line in raw.splitlines() if line.strip())
    elif ext == ".ipynb":
        data = json.loads(src.read_text(encoding="utf-8", errors="ignore"))
        parts = ["".join(c.get("source", [])) for c in data.get("cells", []) if c.get("cell_type") in ("markdown", "code")]
        text = "\n\n".join(parts)
    elif ext == ".eml":
        msg = email.message_from_bytes(src.read_bytes(), policy=policy.default)
        body = msg.get_body(preferencelist=('plain', 'html'))
        if body:
            content = body.get_content()
            if body.get_content_type() == 'text/html':
                text = BeautifulSoup(content, "html.parser").get_text("\n")
            else:
                text = content
    elif ext == ".xml":
        import xml.etree.ElementTree as ET
        tree = ET.parse(src)
        text = "\n".join(elem.text.strip() for elem in tree.getroot().iter() if elem.text and elem.text.strip())
    dst.write_text(text, encoding="utf-8")
