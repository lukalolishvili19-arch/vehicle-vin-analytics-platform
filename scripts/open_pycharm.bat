@echo off
set PROJECT=C:\Users\Ideapad Pro5i\Projects\vehicle-vin-analytics-platform
where pycharm64.exe >nul 2>&1 && (
  start "" pycharm64.exe "%PROJECT%"
  exit /b 0
)
where pycharm.exe >nul 2>&1 && (
  start "" pycharm.exe "%PROJECT%"
  exit /b 0
)
echo PyCharm not found in PATH.
echo Open manually: File -^> Open -^> %PROJECT%
start "" notepad "%PROJECT%\docs\pycharm-thesis-demo.md"
