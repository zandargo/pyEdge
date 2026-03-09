# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for pyEdge
# Build with:  pyinstaller pyedge.spec
#
# Network-drive deployment notes:
#   - UPX is intentionally disabled: on a LAN the decompression CPU overhead
#     exceeds the transfer savings, slowing every DLL load.
#   - Use launch_local.bat on the share so end-users run from %LOCALAPPDATA%.
#   - For best startup performance consider the Nuitka build (build_nuitka.bat).

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('ref',           'ref'),
        ('assets',        'assets'),
        ('translations',  'translations'),
        *collect_data_files('ezdxf'),
        *collect_data_files('shapely'),
        *collect_data_files('numpy'),
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
        'ezdxf.lldxf',              # Low-level DXF parsing (critical for ezdxf)
        'ezdxf.layouts',            # Layout handling
        'ezdxf.sections',           # DXF sections
        *collect_submodules('ezdxf'),
        *collect_submodules('shapely'),
        *collect_submodules('numpy'),
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
