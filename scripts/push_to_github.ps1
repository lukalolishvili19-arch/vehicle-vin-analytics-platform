param(
    [Parameter(Mandatory = $true)]
    [string]$GitHubUsername,
    [string]$RepoName = "vehicle-vin-analytics-platform"
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "Git not found. Install from https://git-scm.com/download/win and restart terminal."
    exit 1
}

if (-not (Test-Path .git)) {
    git init
    git branch -M main
}

git add .
git status --short

$hasChanges = git status --porcelain
if ($hasChanges) {
    git commit -m "feat: VIN analytics platform — Python ETL, MySQL, Power BI docs"
} else {
    Write-Host "Nothing to commit (already clean)."
}

$remoteUrl = "https://github.com/$GitHubUsername/$RepoName.git"
$remotes = git remote 2>$null
if ($remotes -contains "origin") {
    git remote set-url origin $remoteUrl
} else {
    git remote add origin $remoteUrl
}

Write-Host ""
Write-Host "Pushing to $remoteUrl"
Write-Host "Create empty repo first: https://github.com/new?name=$RepoName"
Write-Host ""
git push -u origin main
