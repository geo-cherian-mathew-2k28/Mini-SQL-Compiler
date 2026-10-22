@echo off
setlocal EnableDelayedExpansion

:: Ensure working directory is the script repository root
cd /d "%~dp0"

:: Check if Python is installed in PATH
set "PYTHON_CMD="
where python >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PYTHON_CMD=python"
) else (
    where py >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        set "PYTHON_CMD=py"
    )
)

if not defined PYTHON_CMD (
    echo.
    echo ===============================================================================
    echo [ERROR] Python is not installed or not found in system PATH.
    echo ===============================================================================
    echo Python 3.8 or higher is required to run the Mini SQL Compiler.
    echo Please install Python from https://www.python.org/downloads/
    echo and ensure "Add Python to PATH" is checked during installation.
    echo ===============================================================================
    echo.
    pause
    exit /b 1
)

:: Direct argument shortcut support (e.g., start_studio.bat cli)
if /i "%~1"=="web" goto LAUNCH_WEB
if /i "%~1"=="cli" goto LAUNCH_CLI
if /i "%~1"=="exit" goto EXIT_LAUNCHER

:MENU
cls
echo ===============================================================================
echo                   MINI SQL COMPILER - QUICK LAUNCHER
echo          3rd Year B.Tech CSE - Compiler Design Mini-Project
echo ===============================================================================
echo.
echo Select Execution Mode:
echo   [1] Start Web Studio IDE (Default - opens browser at http://127.0.0.1:5000)
echo   [2] Launch Interactive CLI REPL
echo   [3] Exit
echo.

set "choice=1"
set /p "choice=Enter option [1-3] (Default: 1): "

:: Remove any extra spaces
set "choice=%choice: =%"

if "%choice%"=="1" goto LAUNCH_WEB
if "%choice%"=="2" goto LAUNCH_CLI
if "%choice%"=="3" goto EXIT_LAUNCHER
if /i "%choice%"=="q" goto EXIT_LAUNCHER

echo.
echo [-] Invalid selection '%choice%'. Please choose 1, 2, or 3.
ping 127.0.0.1 -n 2 >nul
goto MENU

:LAUNCH_WEB
echo.
echo [INFO] Starting Mini SQL Compiler Web Studio IDE...
echo [INFO] Server running at http://127.0.0.1:5000
echo [INFO] Press Ctrl+C in this console to terminate the server.
echo.
"%PYTHON_CMD%" run.py
goto SESSION_END

:LAUNCH_CLI
echo.
echo [INFO] Launching Mini SQL Compiler Interactive CLI REPL...
echo [INFO] Type .exit or .quit to leave the CLI shell.
echo.
"%PYTHON_CMD%" run.py --cli
goto SESSION_END

:EXIT_LAUNCHER
echo.
echo Exiting launcher.
endlocal
exit /b 0

:SESSION_END
echo.
echo Session completed. Press any key to close this window...
pause >nul
endlocal
exit /b 0
