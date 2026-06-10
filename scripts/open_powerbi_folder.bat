@echo off
cd /d "%~dp0.."
C:\msys64\ucrt64\bin\python.exe powerbi\generate_html_dashboard.py
start "" "%~dp0..\powerbi\dashboard\vin-analytics.html"
start "" notepad "%~dp0..\powerbi\BUILD_VISUALS.md"
