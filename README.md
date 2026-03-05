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

You can package pyEdge into a standalone Windows executable using **PyInstaller**.  
The `pyedge.spec` file at the project root already has all the correct settings.

### Prerequisites

- Virtual environment activated (see Quick Start above)
- All dependencies installed (`pip install -r requirements.txt`)

### Build (one-folder distribution — recommended)

```powershell
pyinstaller pyedge.spec
```

This creates a `dist\pyEdge\` folder containing `pyEdge.exe` plus all required DLLs and data files. Ship the entire `dist\pyEdge\` folder.

### Output location

```
dist/
└── pyEdge/
    ├── pyEdge.exe       ← launch this
    ├── assets/
    ├── ref/
    ├── translations/
    └── ...              ← bundled runtimes / Qt plugins
```

### Clean previous builds

```powershell
Remove-Item -Recurse -Force build, dist
```

### Notes

| Topic | Detail |
|---|---|
| **Solid Edge** | Must be installed on the target machine — pyEdge communicates with it via COM, which cannot be bundled |
| **Antivirus false positives** | PyInstaller executables are sometimes flagged by AV software; you may need to add an exception for `dist\pyEdge\pyEdge.exe` |
| **UPX compression** | The spec enables UPX if it is on your `PATH`; install it from [upx.github.io](https://upx.github.io) to reduce file size, or set `upx=False` in the spec to skip it |
| **Console window** | The spec sets `console=False` — no black terminal window will appear when launching the app |
| **Icon** | `assets/icons/pyEdge001.png` is used as the application icon; PyInstaller 6+ converts it to `.ico` automatically |

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
