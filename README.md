# pyEdge ✨

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Platform Windows](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![Last Commit](https://img.shields.io/github/last-commit/zandargo/pyEdge)](https://github.com/zandargo/pyEdge/commits/main)
[![GitHub Stars](https://img.shields.io/github/stars/zandargo/pyEdge?style=social)](https://github.com/zandargo/pyEdge/stargazers)

> A modern Python desktop helper for connecting to your active Solid Edge document.

> [!WARNING]
> pyEdge is in **early development**. Features and UI behavior may change frequently, and some flows are still experimental.

`pyEdge` is a lightweight PyQt app with a clean Fluent-style interface. Open Solid Edge, click one button, and it reads your active document name via COM.

## Project Status 🚧

- Current stage: **Early development / prototype**
- APIs and UI details are still evolving
- Bug reports and feedback are welcome while the project matures

## Why pyEdge? 🚀

- Sleek frameless UI (PyQt5 + QFluentWidgets)
- One-click active document scan
- Worker thread keeps the UI responsive
- Friendly status states: `Ready`, `Processing`, `Success`, `Error`

## Tech Stack 🧰

- Python 3.10+ (3.11 recommended)
- PyQt5
- PyQt-Fluent-Widgets
- pywin32 (COM bridge)
- Windows 10/11 + Solid Edge installed

## Quick Start ⚡

### 1. Clone the repo

```powershell
git clone https://github.com/zandargo/pyEdge
cd pyEdge
```

### 2. Create a virtual environment

```powershell
python -m venv venv
```

### 3. Activate it

PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

CMD:

```bat
venv\Scripts\activate.bat
```

### 4. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Run the app

```powershell
python main.py
```

## Building the Executable 📦

Two build paths are available. **Nuitka is recommended** for the fastest startup, especially on mapped network drives.

### Prerequisites (both paths)

- Virtual environment activated (see Quick Start above)
- All dependencies installed (`pip install -r requirements.txt`)

---

### Option A — Nuitka (recommended) 🏆

Nuitka compiles Python to native machine code (C), which eliminates interpreter bootstrap overhead and significantly reduces startup time.

**Extra prerequisites:**

- `pip install nuitka`
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) (MSVC) **or** MinGW-w64 on your `PATH`

**Build:**

```bat
build_nuitka.bat
```

**Output:**

```
dist_nuitka\
└── main.dist\
    ├── pyEdge.exe       ← launch this
    ├── assets/
    ├── ref/
    ├── translations/
    └── ...              ← compiled extension modules + Qt plugins
```

Deploy the entire `main.dist\` folder.

---

### Option B — PyInstaller (fallback)

```powershell
pyinstaller pyedge.spec
```

Output goes to `dist\pyEdge\`. Ship the entire `dist\pyEdge\` folder.

> [!NOTE]
> UPX compression is **disabled** in the spec. On LAN / mapped drives, UPX decompression overhead hurts startup more than the smaller transfer size helps.

---

### Clean previous builds

```powershell
# PyInstaller
Remove-Item -Recurse -Force build, dist

# Nuitka
Remove-Item -Recurse -Force dist_nuitka, main.build
```

### Build notes

| Topic | Detail |
|---|---|
| **Solid Edge** | Must be installed on the target machine — COM cannot be bundled |
| **Antivirus false positives** | Both PyInstaller and Nuitka executables can be flagged by AV; add an exception for the `.exe` if needed |
| **Console window** | Both builds suppress the console window (`--windows-disable-console` / `console=False`) |
| **Icon** | `assets/icons/pyEdge001.ico` is used as the application icon |

## Network Drive Deployment 🌐

Three deployment options are available, from simplest to most polished:

---

### Option 1 — True Windows Installer (recommended) ✅

`build_installer.bat` produces a single **`pyEdge_Setup.exe`** using [Inno Setup](https://jrsoftware.org/isinfo.php) (free).  
Place it on the network share — users double-click it once and they're done.

**What the installer does:**

- Extracts pyEdge to `%LOCALAPPDATA%\Programs\pyEdge` (no admin rights needed)
- Creates a **Start Menu** entry
- Optionally creates a **Desktop shortcut** (user chooses during install)
- Registers an **uninstaller** in *Apps & Features*

**Prerequisites:**

- Build the app first (`build_pyinstaller.bat` or `build_nuitka.bat`)
- Install **Inno Setup 6** on the build machine (one-time setup):

  1. Download the installer from **<https://jrsoftware.org/isdl.php>**  
     *(click "Download Inno Setup X.X.X" — the stable release)*
  2. Run `innosetup-X.X.X.exe` and follow the wizard (all defaults are fine).
  3. After installation `iscc.exe` will be at:  
     `C:\Program Files (x86)\Inno Setup 6\iscc.exe`  
     `build_installer.bat` detects this path automatically — no extra configuration needed.

**Build:**

```bat
build_installer.bat
```

**Deploy:**

```bat
:: Copy the single setup file to the share
copy installer\pyEdge_Setup.exe \\server\share\pyEdge\
```

Users run `pyEdge_Setup.exe` directly from the share — the installer extracts to their local drive, so the app starts instantly every time.

---

### Option 2 — launch_local.bat (no installer required)

Use this if you want to skip the installer step and just robocopy the app folder to the share.

1. Deploy the build output (`dist\pyEdge\` or `dist_nuitka\main.dist\`) to the share.
2. Copy `launch_local.bat` into the same folder.
3. Users double-click **`launch_local.bat`** (or a desktop shortcut to it).

**How it works:**

- On first run it copies all files to `%LOCALAPPDATA%\pyEdge` (local SSD).
- On subsequent runs `robocopy` checks for changed files (sub-second when nothing changed).
- The app always launches from the **local SSD** — zero network I/O during startup.

```
\\server\share\pyEdge\          ← source of truth on the share
    pyEdge.exe
    launch_local.bat            ← users run this
    assets\  ref\  translations\  ...

%LOCALAPPDATA%\pyEdge\          ← synced automatically, launched from here
    pyEdge.exe
    assets\  ref\  translations\  ...
```

---

### Option 3 — Direct from share (not recommended)

Running `pyEdge.exe` directly from a mapped network drive causes slow startup because every DLL read is a network round-trip. Avoid this for regular use.

## Project Layout 🗂️

```text
pyEdge/
|-- app_ui.py
|-- main.py
|-- models/
|   `-- document_info.py
|-- ui/
|   |-- components/
|   |   |-- document_panel.py
|   |   |-- navigation_panel.py
|   |   `-- title_bar.py
|   |-- main_window.py
|   `-- styles.py
|-- workers/
|   `-- solid_edge_worker.py
|-- requirements.txt
|-- services/
|   `-- solid_edge.py
`-- .gitignore
```

## How It Works 🔍

- `main.py`: starts the Qt app and opens the main window.
- `ui/main_window.py`: top-level window orchestration and interaction flow.
- `ui/components/*`: reusable UI building blocks (title bar, nav panel, document panel).
- `ui/styles.py`: centralized Qt stylesheet.
- `workers/solid_edge_worker.py`: background COM operations.
- `models/document_info.py`: typed document model shared across layers.
- `services/solid_edge.py`: Solid Edge COM access and document operations.
- `app_ui.py`: compatibility shim for old imports.

## Troubleshooting 🛠️

### "Solid Edge must be open with an active document"

- Open Solid Edge first.
- Open (or create) any document.
- Try `Scan Active Document` again.

### `ModuleNotFoundError`

Your venv is probably not active, or packages were not installed:

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Notes ✅

- `.gitignore` is already set up to ignore `venv`, `__pycache__`, and other Python artifacts.
- This app is Windows-focused because Solid Edge COM automation requires Windows.
