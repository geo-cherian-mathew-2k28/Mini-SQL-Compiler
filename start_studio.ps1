<#
.SYNOPSIS
    Mini SQL Compiler - Quick Execution Launcher (PowerShell)

.DESCRIPTION
    One-click launcher for the Mini SQL Compiler.
    Allows launching the interactive Web IDE Studio or the terminal CLI REPL
    without requiring manual command-line arguments.

.PARAMETER Mode
    Optional execution mode: 'web', 'cli', or 'exit'.
    If omitted, an interactive menu is presented.

.EXAMPLE
    .\start_studio.ps1

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\start_studio.ps1
#>

[CmdletBinding()]
param (
    [ValidateSet("web", "cli", "exit", "")]
    [string]$Mode = ""
)

# Set working directory to the repository root where this script resides
Set-Location -Path $PSScriptRoot

function Write-Banner {
    Write-Host "===============================================================================" -ForegroundColor Cyan
    Write-Host "                   MINI SQL COMPILER - QUICK LAUNCHER                          " -ForegroundColor Cyan
    Write-Host "          3rd Year B.Tech CSE - Compiler Design Mini-Project                   " -ForegroundColor DarkCyan
    Write-Host "===============================================================================" -ForegroundColor Cyan
}

# 1. Detect Python environment
$pythonCmd = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonCmd = "py"
}

if (-not $pythonCmd) {
    Write-Host ""
    Write-Host "===============================================================================" -ForegroundColor Red
    Write-Host " [ERROR] Python is not installed or not found in system PATH." -ForegroundColor Red
    Write-Host "===============================================================================" -ForegroundColor Red
    Write-Host " Python 3.8 or higher is required to run the Mini SQL Compiler." -ForegroundColor Yellow
    Write-Host " Please install Python from https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host " and ensure 'Add Python to PATH' is checked during installation." -ForegroundColor Yellow
    Write-Host "===============================================================================" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# 2. Resolve launch mode (from parameter or interactive prompt)
$interactive = $false
if ([string]::IsNullOrWhiteSpace($Mode)) {
    $interactive = $true
    while ($true) {
        Clear-Host
        Write-Banner
        Write-Host ""
        Write-Host "Select Execution Mode:" -ForegroundColor Yellow
        Write-Host "  [1] Start Web Studio IDE (Default - opens http://127.0.0.1:5000)" -ForegroundColor Green
        Write-Host "  [2] Launch Interactive CLI REPL" -ForegroundColor Green
        Write-Host "  [3] Exit" -ForegroundColor DarkGray
        Write-Host ""

        $inputChoice = Read-Host "Enter option [1-3, Default=1]"
        if ([string]::IsNullOrWhiteSpace($inputChoice)) {
            $inputChoice = "1"
        }
        $inputChoice = $inputChoice.Trim()

        if ($inputChoice -eq "1" -or $inputChoice -like "*web*") {
            $Mode = "web"
            break
        } elseif ($inputChoice -eq "2" -or $inputChoice -like "*cli*") {
            $Mode = "cli"
            break
        } elseif ($inputChoice -eq "3" -or $inputChoice -like "*exit*" -or $inputChoice -eq "q") {
            $Mode = "exit"
            break
        } else {
            Write-Host "`n[!] Invalid selection '$inputChoice'. Please choose 1, 2, or 3.`n" -ForegroundColor Red
            Start-Sleep -Seconds 1
        }
    }
}

# 3. Execute selected mode
switch ($Mode.ToLower()) {
    "web" {
        Write-Host "`n[INFO] Starting Mini SQL Compiler Web Studio IDE..." -ForegroundColor Green
        Write-Host "[INFO] Server running at http://127.0.0.1:5000" -ForegroundColor Cyan
        Write-Host "[INFO] Press Ctrl+C in this console to terminate the server.`n" -ForegroundColor DarkGray
        & $pythonCmd run.py
    }
    "cli" {
        Write-Host "`n[INFO] Launching Mini SQL Compiler Interactive CLI REPL..." -ForegroundColor Green
        Write-Host "[INFO] Type .exit or .quit to leave the CLI shell.`n" -ForegroundColor DarkGray
        & $pythonCmd run.py --cli
    }
    "exit" {
        Write-Host "`nExiting launcher. Goodbye!`n" -ForegroundColor Yellow
        exit 0
    }
}

if ($interactive) {
    Write-Host "`nSession completed. Press Enter to close this window..." -ForegroundColor DarkGray
    [void](Read-Host)
}
