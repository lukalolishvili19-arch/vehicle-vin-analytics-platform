@echo off
cd /d "%~dp0.."
C:\msys64\ucrt64\bin\python.exe excel\generate_workbook_stdlib.py
if exist excel\output\vehicle_analytics.xlsx start "" excel\output\vehicle_analytics.xlsx
