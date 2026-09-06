@echo off
echo ========================================================
echo   Radar Research Paper Agent - Full Stack Starter
echo ========================================================

echo [1/3] Checking synthetic radar data...
if not exist "backend\data\radar_data\sar_data_iwr1843.npy" (
    echo Generating synthetic SAR data for IWR1843BOOST...
    python backend\generate_synthetic_data.py
)

echo [2/3] Starting FastAPI Backend on http://localhost:8000 ...
start "Radar Agent Backend" cmd /k "cd backend && call venv\Scripts\activate && python run.py"

echo [3/3] Starting Next.js Frontend on http://localhost:3000 ...
start "Radar Agent Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================================
echo   All services launched!
echo   Frontend: http://localhost:3000
echo   Backend:  http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo ========================================================
