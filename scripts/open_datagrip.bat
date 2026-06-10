@echo off
REM Open this project in DataGrip (pre-configured MySQL connection in .idea/)
set PROJECT=%~dp0..
for %%D in (
  "C:\Program Files\JetBrains\DataGrip 2025.3\bin\datagrip64.exe"
  "C:\Program Files\JetBrains\DataGrip 2025.2\bin\datagrip64.exe"
  "C:\Program Files\JetBrains\DataGrip 2025.1\bin\datagrip64.exe"
  "C:\Program Files\JetBrains\DataGrip 2024.3\bin\datagrip64.exe"
) do (
  if exist %%D (
    start "" %%D "%PROJECT%"
    echo DataGrip opened with project: %PROJECT%
    echo Connection: vehicle_analytics@localhost (vehicle_user / changeme)
    exit /b 0
  )
)
echo DataGrip not found. Open manually: File - Open - %PROJECT%
pause
