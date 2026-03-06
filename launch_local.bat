@echo off
setlocal

:: ============================================================
:: pyEdge Network-Share Launcher
::
:: Place this file alongside pyEdge.exe (or main.dist\) on the
:: mapped network drive.  On launch it:
::   1. Syncs only changed files from the share to a local
::      cache in %LOCALAPPDATA%\pyEdge  (robocopy skips files
::      that are already identical — sub-second on no change)
::   2. Runs pyEdge from the local cache, so startup reads
::      DLLs from the local SSD instead of the network.
::
:: First run:  slightly slower (copies the full folder)
:: Every run after:  reads network only to check timestamps,
::                   then launches from local disk instantly.
:: ============================================================

set "APP_NAME=pyEdge"
set "APP_EXE=%APP_NAME%.exe"
set "SOURCE=%~dp0"
set "DEST=%LOCALAPPDATA%\%APP_NAME%"

:: Sync changed files from the network share to the local cache.
:: /E   = include sub-directories (even empty ones)
:: /NP  = no progress percentage (quieter output)
:: /NJH = no job header
:: /NJS = no job summary
:: /NFL = no file list
:: /NDL = no directory list
:: robocopy exit codes 0-7 are all success (0 = nothing to do, 1 = files copied).
robocopy "%SOURCE%" "%DEST%" /E /NP /NJH /NJS /NFL /NDL 2>nul

if %ERRORLEVEL% GTR 7 (
    echo [pyEdge Launcher] WARNING: file sync had errors ^(robocopy exit %ERRORLEVEL%^).
    echo Running from network share as fallback...
    start "" "%SOURCE%%APP_EXE%"
    exit /b
)

:: Run from the local SSD cache — no network I/O during startup
start "" "%DEST%\%APP_EXE%"
