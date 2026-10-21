# Peel

Peel is an offline desktop utility that converts arbitrary document, ebook, and markup formats into clean, unformatted UTF-8 plain text. 

It wraps Calibre's ebook tools, Pandoc, and native Python parsers into a standalone PySide6 interface to bypass manual CLI invocation and online converters.

![Platform](https://img.shields.io/badge/Platform-Linux%20(x86__64)-grey?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.10+-grey?style=flat-square)
![GUI](https://img.shields.io/badge/GUI-Qt6%20%2F%20PySide6-grey?style=flat-square)
![License](https://img.shields.io/badge/License-GPL--3.0-grey?style=flat-square)

---

## Technical Specifications

Peel inspects incoming files and routes them through isolated internal extraction pipelines based on MIME type and structure:

| Format Category | Handled Extensions | Parser Backend | Output Characteristics |
| :--- | :--- | :--- | :--- |
| **E-Books** | `.epub`, `.mobi`, `.azw3`, `.fb2`, `.lit` | Calibre Engine | Structural stripping, chapter-ordered text stream |
| **Compound Documents** | `.docx`, `.odt`, `.rtf` | Pandoc | Strips styling/tables to linear markdown-like flow |
| **Paged Documents** | `.pdf` | PyPDF | Raw character stream extraction |
| **Spreadsheets** | `.xlsx`, `.xls`, `.ods`, `.csv`, `.tsv` | Native Tabular Parser | Delimited row-by-row plaintext dump |
| **Presentations** | `.pptx`, `.odp` | Native XML Walker | Slide-by-slide body text extraction |
| **Subtitles** | `.srt`, `.vtt`, `.sub`, `.ass` | Regex Parser | Timecodes, tags, and styling markers removed |

---

## Data Pipeline

The conversion workflow operates entirely in-memory and on local storage:

~~~text
[Input Document]
       │
       ▼
 [Format Identification]
       │
       ├── E-Books      ──> Bundled Calibre Driver  ──┐
       ├── Rich Text    ──> Bundled Pandoc Core     ──┼──> [Raw Text Stream]
       ├── PDF / Office ──> Internal Python Parsers ──┘            │
                                                                   ▼
                                                       [Sanitization & Normalization]
                                                        - Strips control chars & nulls
                                                        - Normalizes line endings (LF)
                                                        - Unicode normalization (NFC)
                                                                   │
                                                                   ▼
                                                         [Destination: .txt]
~~~

---

## Pre-built Binaries

Standalone x86_64 AppImages are available on the [Releases](../../releases) page. Dependencies (Qt6 runtimes, Pandoc, and Calibre conversion utilities) are embedded within the image.

~~~bash
chmod +x Peel-x86_64.AppImage
./Peel-x86_64.AppImage
~~~

### Systems with FUSE 3 Defaults (Fedora, Arch, Ubuntu 22.04+)
If the AppImage fails to mount due to standard AppImage FUSE 2 dependencies:

~~~bash
./Peel-x86_64.AppImage --appimage-extract-and-run
~~~

Alternatively, install user-space FUSE 2 compatibility:
* Fedora: `sudo dnf install fuse-libs`
* Debian/Ubuntu: `sudo apt install libfuse2`

---

## Building from Source

### Prerequisites
* Python 3.10+
* System-level Pandoc and Calibre binaries (only required when running directly from source)

### Environment Setup

~~~bash
git clone https://github.com/your-username/peel.git
cd peel

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
~~~

### Running Locally
~~~bash
python main.py
~~~

### Generating the AppImage
Packaging requires `pyinstaller` and `appimagetool`:

~~~bash
pyinstaller peel.spec
./packaging/build-appimage.sh
~~~

---

## License

This software is released under the [GNU General Public License v3.0](LICENSE).
