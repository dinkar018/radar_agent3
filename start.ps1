# Radar Research Paper Agent - PowerShell Starter
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Radar Research Paper Agent - Full Stack Starter" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

# Check synthetic data
if (-not (Test-Path "backend\data\radar_data\sar_data_iwr1843.npy")) {
    Write-Host "[1/3] Generating synthetic SAR data for IWR1843BOOST..." -ForegroundColor Yellow
    python backend\generate_synthetic_data.py
} else {
    Write-Host "[1/3] Synthetic radar data ready." -ForegroundColor Green
}

# Launch backend
Write-Host "[2/3] Starting FastAPI Backend on http://localhost:8000 ..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; .\venv\Scripts\Activate.ps1; python run.py"

# Launch frontend
Write-Host "[3/3] Starting Next.js Frontend on http://localhost:3000 ..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Write-Host ""
Write-Host "========================================================" -ForegroundColor Green
Write-Host "  All services launched!" -ForegroundColor Green
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "  Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "========================================================" -ForegroundColor Green
