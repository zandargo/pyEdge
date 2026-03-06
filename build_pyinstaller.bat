@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo   pyEdge ^| PyInstaller Onedir Build
echo   Optimized for network-drive deployment
echo ============================================================
echo.

:: ---------------------------------------------------------------------------
:: Activate the virtual environment if one exists in the project root.
:: This avoids builds that accidentally pick up the wrong Python or packages.
:: ---------------------------------------------------------------------------
if exist "venv\Scripts\activate.bat" (
    echo [1/4] Activating virtual environment...
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    echo [1/4] Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo [1/4] No venv found — using system Python.
)

:: ---------------------------------------------------------------------------
:: Verify PyInstaller is available before continuing.
:: ---------------------------------------------------------------------------
python -m PyInstaller --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] PyInstaller not found. Install it with:
    echo         pip install pyinstaller
    pause
    exit /b 1
)

:: ---------------------------------------------------------------------------
:: Clean previous build artifacts so the dist folder only contains files
:: that actually belong to this build (avoids shipping orphaned DLLs).
:: ---------------------------------------------------------------------------
echo [2/4] Cleaning previous build...
if exist build  Remove-Item -Recurse -Force build  2>nul
if exist "dist\pyEdge" (
    rmdir /s /q "dist\pyEdge" 2>nul
)

:: ---------------------------------------------------------------------------
:: Build using pyedge.spec
::
:: Key network-deployment settings already in the spec:
::   --onedir   (exclude_binaries=True + COLLECT) — one folder, not one file.
::              --onefile extracts to %TEMP% on every launch which is far
::              slower on a network share; onedir + launch_local.bat is faster.
::   upx=False  — UPX decompression CPU cost outweighs LAN transfer savings.
::   excludes   — stripped of 20+ unused stdlib / scientific packages to
::              reduce the total file count copied to the local SSD cache.
::
:: --clean      — purge PyInstaller's own build cache (Analysis, toc files)
::              to avoid stale module lists leaking between builds.
:: ---------------------------------------------------------------------------
echo [3/4] Running PyInstaller...
echo.
python -m PyInstaller pyedge.spec --clean

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] PyInstaller build failed. Check the output above.
    pause
    exit /b 1
)

echo.
echo [4/4] Build complete!
echo.
echo ============================================================
echo   Output folder: dist\pyEdge\
echo.
echo   Network-drive deployment steps:
echo     1. Copy the entire dist\pyEdge\ folder to the share:
echo           robocopy dist\pyEdge \\server\share\pyEdge /E
echo     2. Copy launch_local.bat into the same share folder.
echo     3. Create a shortcut to launch_local.bat for end-users.
echo        (Do NOT shortcut pyEdge.exe directly on the share.)
echo.
echo   Why launch_local.bat?
echo     It syncs only changed files to %%LOCALAPPDATA%%\pyEdge
echo     then runs pyEdge.exe from the local SSD — zero network
echo     I/O during startup after the first run.
echo ============================================================
pause
