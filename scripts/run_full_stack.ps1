#Requires -Version 5.1
<#
.SYNOPSIS
  Full stack deployment: Docker MySQL -> ETL -> DB -> Power BI export -> GitHub
.USAGE
  .\scripts\run_full_stack.ps1
#>
$ErrorActionPreference = "Continue"
Set-Location $PSScriptRoot\..

Write-Host "`n=== [1/5] Docker MySQL ===" -ForegroundColor Cyan
$docker = Get-Command docker -ErrorAction SilentlyContinue
if ($docker) {
    docker compose up -d
    Write-Host "Waiting 30s for MySQL init..."
    Start-Sleep -Seconds 30
    docker compose ps
} else {
    Write-Warning "Docker not found. Install Docker Desktop: https://www.docker.com/products/docker-desktop/"
}

Write-Host "`n=== [2/5] ETL Pipeline ===" -ForegroundColor Cyan
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { $python = Get-Command python3 -ErrorAction SilentlyContinue }
if (-not $python) { $python = @{ Source = "C:\msys64\ucrt64\bin\python.exe" } }

if (Test-Path $python.Source) {
    & $python.Source -m pip install -r requirements.txt -q 2>$null
    & $python.Source -m pip install -e . -q 2>$null
    & $python.Source -m etl
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Full ETL failed, running stdlib fallback..."
        & $python.Source scripts/run_etl_stdlib.py
    }
} else {
    Write-Error "Python not found."
}

Write-Host "`n=== [3/5] MySQL Load ===" -ForegroundColor Cyan
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
(Get-Content .env) -replace 'LOAD_TO_MYSQL=false', 'LOAD_TO_MYSQL=true' | Set-Content .env
$env:LOAD_TO_MYSQL = "true"
if (Test-Path $python.Source) {
    & $python.Source -m etl
}

Write-Host "`n=== [4/5] Power BI Export ===" -ForegroundColor Cyan
$pbiFile = "powerbi/data/fct_vehicle_inventory.csv"
if (-not (Test-Path $pbiFile) -and (Test-Path $python.Source)) {
    & $python.Source scripts/run_etl_stdlib.py
}
if (Test-Path $pbiFile) {
    Write-Host "Import into Power BI: $((Resolve-Path $pbiFile).Path)" -ForegroundColor Green
} else {
    Write-Host "Use gold_latest.csv from data/gold/vehicle_search/" -ForegroundColor Yellow
}

Write-Host "`n=== [5/5] GitHub ===" -ForegroundColor Cyan
$git = Get-Command git -ErrorAction SilentlyContinue
if ($git) {
    if (-not (Test-Path .git)) { git init; git branch -M main }
    git add -A
    git status --short
    Write-Host @"

Next steps:
  git commit -m "feat: VIN Intelligence platform - ETL, MySQL, Power BI"
  gh repo create vin-intelligence-analytics --public --source=. --push
  # or: git remote add origin https://github.com/USER/REPO.git && git push -u origin main
"@ -ForegroundColor Yellow
} else {
    Write-Warning "Git not found. Install: https://git-scm.com/download/win"
}

Write-Host "`n=== Complete ===" -ForegroundColor Green
