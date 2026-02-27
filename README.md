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

## Project Layout 🗂️

```text
pyEdge/
|-- app_ui.py
|-- main.py
|-- requirements.txt
|-- services/
|   `-- solid_edge.py
`-- .gitignore
```

## How It Works 🔍

- `main.py`: starts the Qt app and opens the main window.
- `app_ui.py`: renders UI and launches a worker for the Solid Edge check.
- `services/solid_edge.py`: connects to `SolidEdge.Application` and reads `ActiveDocument.Name`.

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
