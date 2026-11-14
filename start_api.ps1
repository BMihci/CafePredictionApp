$host.UI.RawUI.WindowTitle = "Kingfool Inc. | AI & Cafe API Server"
Write-Host "========================================================" -ForegroundColor Yellow
Write-Host "KINGFOOL INC. AI & CAFE REST API BACKEND" -ForegroundColor Yellow
Write-Host "========================================================" -ForegroundColor Yellow
Write-Host "Bulut Veritabani : Supabase Bagli" -ForegroundColor Green
Write-Host "API Adresi       : http://localhost:8000" -ForegroundColor Cyan
Write-Host "Swagger Docs     : http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Yellow
Write-Host ""

Set-Location $PSScriptRoot
python api/main.py
