# Re-apply PyCharm Python 3.12 interpreter paths (run if PyCharm breaks SDK again)
$jdkTable = "$env:APPDATA\JetBrains\PyCharm2025.3\options\jdk.table.xml"
$venvPython = "$PSScriptRoot\..\.venv\Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    Write-Error "Missing venv: $venvPython"
    exit 1
}

Write-Host "OK: $(& $venvPython --version)"
Write-Host "PyCharm SDK file: $jdkTable"
Write-Host "Restart PyCharm, then Run -> Load MySQL"
