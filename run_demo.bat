@echo off
REM Mini SQL Compiler — Quickstart Batch Helper for Evaluators
REM Executes the curated 5-query demonstration showcase

python demo_runner.py %*
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Demo runner encountered an error.
)
