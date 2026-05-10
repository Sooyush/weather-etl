# refresh.ps1 — Pull latest weather data then remind you to refresh Power BI

$repoPath = "C:\Users\You\weather-etl"   # ← change this to your actual path

Write-Host "`nPulling latest data from GitHub..." -ForegroundColor Cyan
Set-Location $repoPath
git pull

Write-Host "`nDone! Data is up to date." -ForegroundColor Green
Write-Host "Open Power BI Desktop and click Refresh to load new data.`n" -ForegroundColor Yellow
pause