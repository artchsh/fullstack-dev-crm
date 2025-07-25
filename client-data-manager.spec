# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from pathlib import Path

# Get the source directory
src_dir = Path('src').resolve()

a = Analysis(
    ['src/main.py'],
    pathex=[str(src_dir)],
    binaries=[],
    datas=[
        ('config/app_settings.json', 'config'),
        ('README.md', '.'),
        ('LICENSE', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'ttkbootstrap',
        'sqlalchemy',
        'cryptography',
        'flask',
        'flask_cors',
        'PIL',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='client-data-manager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add path to .ico file here if you have one
)

# Create a directory structure for distribution
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='client-data-manager-dist',
)
