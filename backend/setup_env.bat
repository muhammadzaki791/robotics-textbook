@echo off
echo Setting up virtual environment for RAG Chatbot backend...

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing dependencies from requirements.txt...
pip install -r requirements.txt

echo.
echo Virtual environment setup complete!
echo Virtual environment created in: %cd%\venv
echo Dependencies installed from requirements.txt
echo.
echo To activate the virtual environment in the future:
echo   venv\Scripts\activate.bat
echo.
echo To deactivate:
echo   deactivate
pause