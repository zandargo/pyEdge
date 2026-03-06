@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo   pyEdge ^| Nuitka Standalone Build
echo   Compiles Python to native machine code for fastest startup
echo ============================================================
echo.
echo Prerequisites:
echo   pip install nuitka
echo   MSVC (Visual Studio Build Tools) or MinGW-w64 on PATH
echo.

:: ---------------------------------------------------------------------------
:: Nuitka standalone build
::
:: --standalone           : self-contained output folder (no Python install needed)
:: --enable-plugin=pyqt5  : auto-handles Qt DLL copying and plugin discovery
:: --include-package=...  : force-include packages Nuitka may not detect via
::                          static analysis (dynamic imports, COM dispatch, etc.)
:: --nofollow-import-to=  : prevents Nuitka from compiling unused stdlib / libs,
::                          reducing output size and build time
:: --python-flag=...      : strip docstrings and disable asserts for leaner code
:: --output-dir           : where to put the .dist folder
:: --output-filename      : name of the resulting .exe inside the .dist folder
:: ---------------------------------------------------------------------------

python -m nuitka ^
    --standalone ^
    --windows-disable-console ^
    --enable-plugin=pyqt5 ^
    --include-qt-plugins=sensible,styles,platforms,iconengines,imageformats ^
    --include-package=qfluentwidgets ^
    --windows-icon-from-ico=assets\icons\pyEdge001.ico ^
    --include-data-dir=ref=ref ^
    --include-data-dir=assets=assets ^
    --include-data-dir=translations=translations ^
    --include-module=win32com ^
    --include-module=win32com.client ^
    --include-module=win32com.server ^
    --include-module=win32api ^
    --include-module=win32con ^
    --include-module=pywintypes ^
    --include-module=pythoncom ^
    --nofollow-import-to=tkinter ^
    --nofollow-import-to=matplotlib ^
    --nofollow-import-to=numpy ^
    --nofollow-import-to=scipy ^
    --nofollow-import-to=PIL ^
    --nofollow-import-to=PySide6 ^
    --nofollow-import-to=unittest ^
    --nofollow-import-to=email ^
    --nofollow-import-to=http ^
    --nofollow-import-to=xmlrpc ^
    --nofollow-import-to=pydoc ^
    --nofollow-import-to=multiprocessing ^
    --nofollow-import-to=asyncio ^
    --nofollow-import-to=concurrent ^
    --python-flag=no_docstrings ^
    --output-dir=dist_nuitka ^
    --output-filename=pyEdge ^
    main.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Build failed. Check the output above.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   Build complete!
echo   Output folder: dist_nuitka\main.dist\
echo   Deploy the entire main.dist\ folder to the network share.
echo   Use launch_local.bat alongside it for fastest startup.
echo ============================================================
pause
