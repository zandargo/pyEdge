# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for pyEdge
# Build with:  pyinstaller pyedge.spec

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('ref',           'ref'),
        ('assets',        'assets'),
        ('translations',  'translations'),
    ],
    hiddenimports=[
        'win32com',
        'win32com.client',
        'win32com.server',
        'win32api',
        'win32con',
        'pywintypes',
        'PyQt5.sip',
        'qfluentwidgets',
        'qfluentwidgets.common',
        'qfluentwidgets.components',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'PySide6',
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
        'PIL',
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='pyEdge',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,               # no console window (windowed app)
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icons/pyEdge001.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='pyEdge',
)
