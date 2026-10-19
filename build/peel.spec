# PyInstaller spec for Peel
from pathlib import Path
import sys
import pypandoc
from PyInstaller.utils.hooks import collect_all

project_root = Path(SPECPATH).parent      
app_dir = project_root / "app"
resources = app_dir / "resources"
vendor_dir = project_root / "vendor"

datas = []
binaries = []
hiddenimports = ['pypandoc', 'pypdf']

# پیدا کردن مسیر دقیق pandoc و باندل کردنش
try:
    pandoc_bin = pypandoc.get_pandoc_path()
    if pandoc_bin:
        binaries.append((pandoc_bin, '.'))
except:
    pass

# جمع‌آوری فایل‌های جانبی پکیج‌ها
for pkg in ['pypdf', 'pypandoc']:
    tmp = collect_all(pkg)
    datas += tmp[0]
    binaries += tmp[1]
    hiddenimports += tmp[2]

a = Analysis(
    [str(app_dir / "__main__.py")],
    pathex=[str(project_root)],
    binaries=binaries,
    datas=datas + [
        (str(resources / "icon.svg"), "app/resources"),
        (str(vendor_dir), "vendor"),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "PySide6.QtNetwork", "PySide6.QtQml", "PySide6.QtQuick"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="peel",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="peel",
)
