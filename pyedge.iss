; ============================================================
; pyEdge — Inno Setup installer script
; Compile with: iscc pyedge.iss
; Output: installer\pyEdge_Setup.exe
;
; Design decisions for network-share deployment:
;   - PrivilegesRequired=lowest → installs per-user to
;     %LOCALAPPDATA%\Programs\pyEdge, no admin rights needed.
;   - Compression=lzma2/ultra64 + SolidCompression → the setup
;     EXE itself is small to transfer; extraction is local.
;   - Desktop icon is opt-in (unchecked by default) — users who
;     want it tick the box during install.
;   - Includes an uninstaller registered in "Apps & features".
; ============================================================

#define AppName      "pyEdge"
#define AppVersion   "1.0"
#define AppPublisher "zandargo"
#define AppURL       "https://github.com/zandargo/pyEdge"
#define AppExeName   "pyEdge.exe"
; Path to the PyInstaller onedir output folder
#define SourceDir    "dist\pyEdge"

[Setup]
AppId={{A3F2D8B1-4E6C-4D9F-B0A2-7C5E3F1D8A09}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}/issues
AppUpdatesURL={#AppURL}/releases

; Per-user install — no UAC prompt, works from a read-only share
DefaultDirName={localappdata}\Programs\{#AppName}
; Skip the "Select Start Menu folder" page (we create one entry automatically)
DisableProgramGroupPage=yes
DefaultGroupName={#AppName}

; Output
OutputDir=installer
OutputBaseFilename=pyEdge_Setup
SetupIconFile=assets\icons\pyEdge001.ico

; Compression — best ratio; extraction is done locally, so size >> speed
Compression=lzma2/ultra64
SolidCompression=yes

; UI
WizardStyle=modern
WizardSizePercent=120

; No elevation needed (per-user)
PrivilegesRequired=lowest
; Allow user to elevate if they want a machine-wide install
PrivilegesRequiredOverridesAllowed=dialog

; Minimum Windows version: Windows 10
MinVersion=10.0

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "portuguese"; MessagesFile: "compiler:Languages\Portuguese.isl"

[Tasks]
Name: "desktopicon"; \
    Description: "{cm:CreateDesktopIcon}"; \
    GroupDescription: "{cm:AdditionalIcons}"; \
    Flags: unchecked

[Files]
; Copy entire PyInstaller onedir output — recurse keeps Qt plugins, DLLs, data folders
Source: "{#SourceDir}\*"; \
    DestDir: "{app}"; \
    Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Start Menu
Name: "{autoprograms}\{#AppName}"; \
    Filename: "{app}\{#AppExeName}"; \
    Comment: "pyEdge — Solid Edge document helper"

; Desktop (optional, controlled by the Tasks section above)
Name: "{autodesktop}\{#AppName}"; \
    Filename: "{app}\{#AppExeName}"; \
    Comment: "pyEdge — Solid Edge document helper"; \
    Tasks: desktopicon

[Run]
; Offer to launch pyEdge immediately after installation finishes
Filename: "{app}\{#AppExeName}"; \
    Description: "{cm:LaunchProgram,{#AppName}}"; \
    Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Remove any user-generated config / cache files left behind by the app
Type: filesandordirs; Name: "{localappdata}\{#AppName}\settings"
