# pyEdge

A modern desktop connector UI for Solid Edge, built with Python + PyQt.

`pyEdge` opens a small Fluent-style app that checks your currently active Solid Edge document through COM automation.

## Features

- Clean frameless desktop UI (PyQt5 + QFluentWidgets)
- One-click scan of the active Solid Edge document
- Background worker thread to keep the UI responsive
- Clear status feedback (`Ready`, `Processing`, `Success`, `Error`)

## Requirements

- Windows 10/11
- Python 3.10+ (3.11 recommended)
- Solid Edge installed and running
- An active Solid Edge document open before scanning

## Quick Start

### 1. Clone or open this folder

```powershell
git clone <your-repo-url>
cd pyEdge
```

### 2. Create a virtual environment

```powershell
python -m venv venv
```

### 3. Activate the virtual environment

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

## Project Structure

```text
pyEdge/
|-- app_ui.py
|-- main.py
|-- services/
|   `-- solid_edge.py
`-- .gitignore
```

## How It Works

- `main.py`: boots the Qt application and opens the main window.
- `app_ui.py`: builds the UI and starts a worker thread for Solid Edge checks.
- `services/solid_edge.py`: uses `win32com.client` to connect to `SolidEdge.Application` and read the active document name.

## Common Issues

### `Error: Solid Edge must be open with an active document.`

- Open Solid Edge.
- Open or create a document in Solid Edge.
- Click `Scan Active Document` again.

### `ModuleNotFoundError`

Your virtual environment is likely not active, or dependencies are not installed.

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Git Setup (Optional)

If you want to initialize this as a new repository:

```powershell
git init
git add .
git commit -m "Initial commit"
```

The existing `.gitignore` is already configured to exclude `venv`, `__pycache__`, and other Python-generated files.
