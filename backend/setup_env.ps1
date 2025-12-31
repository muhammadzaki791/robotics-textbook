# PowerShell script to set up virtual environment for RAG Chatbot backend

Write-Host "Setting up virtual environment for RAG Chatbot backend..." -ForegroundColor Green

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install requirements
Write-Host "Installing dependencies from requirements.txt..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host "" -ForegroundColor Green
Write-Host "Virtual environment setup complete!" -ForegroundColor Green
Write-Host "Virtual environment created in: $((Get-Location).Path)\venv" -ForegroundColor Green
Write-Host "Dependencies installed from requirements.txt" -ForegroundColor Green
Write-Host "" -ForegroundColor Green
Write-Host "To activate the virtual environment in the future:" -ForegroundColor Green
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor Green
Write-Host "" -ForegroundColor Green
Write-Host "To deactivate:" -ForegroundColor Green
Write-Host "  deactivate" -ForegroundColor Green