@echo off
REM Start the Momo SMS Data API server with virtual environment (Windows)

echo Starting Momo SMS Data API...
echo.

REM Check if venv exists
if not exist "venv" (
    echo Virtual environment not found. Creating...
    python -m venv venv
    echo [OK] Virtual environment created
    echo.
)

REM Activate venv
call venv\Scripts\activate.bat

REM Check if dependencies are installed
python -c "import apispec" 2>nul
if errorlevel 1 (
    echo Installing dependencies...
    python -m pip install --upgrade pip -q
    pip install -r requirements.txt -q
    echo [OK] Dependencies installed
    echo.
)

REM Stop any existing server
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *main.py*" >nul 2>&1

REM Start the server
echo Server starting...
echo.
python main.py
