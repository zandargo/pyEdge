# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for pyEdge
# Build with:  pyinstaller pyedge.spec
#
# Network-drive deployment notes:
#   - UPX is intentionally disabled: on a LAN the decompression CPU overhead
#     exceeds the transfer savings, slowing every DLL load.
#   - Use launch_local.bat on the share so end-users run from %LOCALAPPDATA%.
#   - For best startup performance consider the Nuitka build (build_nuitka.bat).

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
        # GUI alternatives
        'PySide6',
        'tkinter',
        # Scientific / image libs not used at runtime
        'matplotlib',
        'numpy',
        'scipy',
        'PIL',
        # Standard-library extras that pull in large dependency trees
        'email',
        'html',
        'http',
        'unittest',
        'xmlrpc',
        'pydoc',
        'doctest',
        'ftplib',
        'smtplib',
        'telnetlib',
        'imaplib',
        'poplib',
        'nntplib',
        'mailbox',
        'msilib',
        'cgi',
        'cgitb',
        'turtle',
        'turtledemo',
        'py_compile',
        'compileall',
        'multiprocessing',
        'concurrent',
        'asyncio',
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
    upx=False,            # disabled — decompression overhead hurts network-share startup
    console=False,        # no console window (windowed app)
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
    upx=False,            # disabled — decompression overhead hurts network-share startup
    upx_exclude=[],
    name='pyEdge',
)
