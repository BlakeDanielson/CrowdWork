# CrowdWork Development Environment Launcher
Write-Host "Starting CrowdWork development environment..." -ForegroundColor Green

# Start Backend Server (in a new PowerShell window)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd $PSScriptRoot; cd backend; if (-Not (Test-Path venv)) { Write-Host 'Creating virtual environment...' -ForegroundColor Yellow; python -m venv venv }; .\venv\Scripts\Activate.ps1; if (-Not (Test-Path venv\Scripts\uvicorn.exe)) { Write-Host 'Installing dependencies...' -ForegroundColor Yellow; pip install -r requirements.txt }; Write-Host 'Starting FastAPI server...' -ForegroundColor Green; uvicorn main:app --reload"

# Start Frontend Server (in this window)
Write-Host "Starting React development server..." -ForegroundColor Green
cd $PSScriptRoot\frontend
if (-Not (Test-Path node_modules)) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    npm install
}
npm run dev 