@echo off
REM =============================================================================
REM Full stack: Docker MySQL -> ETL -> DB Load -> Power BI export -> Git push
REM Run from project root: scripts\run_full_stack.bat
REM =============================================================================
setlocal enabledelayedexpansion
cd /d "%~dp0.."

echo [1/5] DOCKER MYSQL
where docker >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Docker not found in PATH. Install Docker Desktop and re-run.
    echo Skipping docker compose...
) else (
    docker compose up -d
    echo Waiting for MySQL to be healthy...
    timeout /t 25 /nobreak >nul
)

echo.
echo [2/5] ETL - Python environment
where python >nul 2>&1
if %errorlevel% equ 0 (
    python -m pip install -r requirements.txt -q 2>nul
    python -m pip install -e . -q 2>nul
    python -m etl
) else (
    echo Using stdlib ETL fallback...
    C:\msys64\ucrt64\bin\python.exe scripts\run_etl_stdlib.py 2>nul
    if !errorlevel! neq 0 py scripts\run_etl_stdlib.py
)

echo.
echo [3/5] DB LOAD
set LOAD_TO_MYSQL=true
if exist .env (
    findstr /C:"LOAD_TO_MYSQL=true" .env >nul || echo LOAD_TO_MYSQL=true>>.env
) else (
    copy .env.example .env >nul
    powershell -Command "(Get-Content .env) -replace 'LOAD_TO_MYSQL=false','LOAD_TO_MYSQL=true' | Set-Content .env"
)
where python >nul 2>&1
if %errorlevel% equ 0 (
    set LOAD_TO_MYSQL=true
    python -m etl
) else (
    echo Skipping MySQL load - Python ETL with pymysql required.
    echo Import powerbi\data\fct_vehicle_inventory.csv into Power BI instead.
)

echo.
echo [4/5] POWER BI export
if not exist powerbi\data\fct_vehicle_inventory.csv (
    python scripts\run_etl_stdlib.py 2>nul
)
echo Power BI file: powerbi\data\fct_vehicle_inventory.csv
echo Open Power BI Desktop - Get Data - Text/CSV - select file above.
echo Or connect MySQL: localhost:3306 / vehicle_analytics

echo.
echo [5/5] GITHUB
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Git not in PATH. Install Git for Windows.
    goto :done
)
if not exist .git git init
git add -A
git status
echo.
echo To commit and push:
echo   git commit -m "feat: complete VIN analytics platform ETL-DB-PowerBI"
echo   gh repo create vin-analytics-platform --public --source=. --push
echo   OR: git remote add origin YOUR_URL ^&^& git push -u origin main

:done
echo.
echo === DONE ===
endlocal
