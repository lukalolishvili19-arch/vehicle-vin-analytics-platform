@echo off
cd /d "%~dp0.."
".venv\Scripts\python.exe" scripts\load_mysql_stdlib.py
pause
