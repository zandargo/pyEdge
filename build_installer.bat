@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo   pyEdge ^| Full Installer Build
echo   PyInstaller (onedir) + Inno Setup → pyEdge_Setup.exe
echo ============================================================
echo.

:: ---------------------------------------------------------------------------
:: Step 1 — Activate virtual environment
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
:: Step 2 — Verify required Python packages
:: ---------------------------------------------------------------------------
python -m pip show pyinstaller >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] PyInstaller not found. Install it with:
    echo         pip install pyinstaller
    pause
    exit /b 1
)

python -m pip show ezdxf >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] ezdxf not found. Install it with:
    echo         pip install ezdxf
    pause
    exit /b 1
)

python -m pip show shapely >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] shapely not found. Install it with:
    echo         pip install shapely
    pause
    exit /b 1
)

python -m pip show numpy >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] numpy not found. Install it with:
    echo         pip install numpy
    pause
    exit /b 1
)

:: ---------------------------------------------------------------------------
:: Step 3 — Locate Inno Setup compiler (iscc.exe)
::   Common install paths for Inno Setup 6; update if yours differs.
:: ---------------------------------------------------------------------------
set "ISCC="
for %%P in (
    "C:\Program Files (x86)\Inno Setup 6\iscc.exe"
    "C:\Program Files\Inno Setup 6\iscc.exe"
    "C:\Program Files (x86)\Inno Setup 5\iscc.exe"
    "C:\Program Files\Inno Setup 5\iscc.exe"
	 "C:\Users\madson.unias\AppData\Local\Programs\Inno Setup 6\ISCC.exe"
) do (
    if exist %%P (
        set "ISCC=%%~P"
        goto :found_iscc
    )
)

echo.
echo [ERROR] Inno Setup compiler (iscc.exe) not found.
echo.
echo   Download Inno Setup (free) from: https://jrsoftware.org/isinfo.php
echo   Install it, then re-run this script.
pause
exit /b 1

:found_iscc
echo [1/4] Inno Setup found: %ISCC%
echo.

:: ---------------------------------------------------------------------------
:: Step 4 — Clean previous build artifacts
:: ---------------------------------------------------------------------------
echo [2/4] Cleaning previous build artifacts...
if exist build     rmdir /s /q build
if exist "dist\pyEdge" rmdir /s /q "dist\pyEdge"
if exist installer rmdir /s /q installer

:: ---------------------------------------------------------------------------
:: Step 5 — Build PyInstaller onedir distribution
:: ---------------------------------------------------------------------------
echo [3/4] Building with PyInstaller...
echo.
python -m PyInstaller pyedge.spec --clean

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] PyInstaller build failed. Check the output above.
    pause
    exit /b 1
)

:: Verify the expected output exists before handing to Inno Setup
if not exist "dist\pyEdge\pyEdge.exe" (
    echo.
    echo [ERROR] dist\pyEdge\pyEdge.exe not found after PyInstaller build.
    pause
    exit /b 1
)

:: ---------------------------------------------------------------------------
:: Step 6 — Compile Inno Setup installer
:: ---------------------------------------------------------------------------
echo.
echo [4/4] Compiling Inno Setup installer...
echo.
"%ISCC%" pyedge.iss

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Inno Setup compilation failed. Check the output above.
    pause
    exit /b 1
)

:: ---------------------------------------------------------------------------
:: Done
:: ---------------------------------------------------------------------------
echo.
echo ============================================================
echo   Installer ready: installer\pyEdge_Setup.exe
echo.
echo   Network-share deployment:
echo     1. Copy installer\pyEdge_Setup.exe to the share.
echo     2. Users double-click pyEdge_Setup.exe from the share.
echo     3. The installer:
echo          - Extracts pyEdge to %%LOCALAPPDATA%%\Programs\pyEdge
echo          - Creates a Start Menu entry
echo          - Optionally creates a Desktop shortcut
echo          - Registers an uninstaller in Apps ^& Features
echo          - Does NOT require administrator rights
echo ============================================================
pause
