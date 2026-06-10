@echo off
cd /d "%~dp0.."
if exist ".venv\Scripts\python.exe" (
  .venv\Scripts\python.exe scripts\run_etl_stdlib.py
) else if exist "..\..venv\Scripts\python.exe" (
  ..\..venv\Scripts\python.exe scripts\run_etl_stdlib.py
) else (
  C:\msys64\ucrt64\bin\python.exe scripts\run_etl_stdlib.py
)
pause
