@echo off
setlocal
cd /d "%~dp0"

echo ==========================================
echo      RALLY STAGE TRACKER
 echo ==========================================

if not exist ".venv\Scripts\python.exe" (
    echo [1/3] Creating virtual environment...
    py -m venv .venv
    if errorlevel 1 (
        echo ERROR: Python is not installed or not available as "py".
        pause
        exit /b 1
    )
)

call ".venv\Scripts\activate.bat"

echo [2/3] Installing dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

if not exist "database\rally_tracker.db" (
    echo Initializing database...
    python init_db.py
    if errorlevel 1 (
        echo ERROR: Database initialization failed.
        pause
        exit /b 1
    )
)

echo [3/3] Starting server...
echo.
echo Open in browser: http://127.0.0.1:5000
 echo Admin login: admin / 1987
 echo To stop the server press Ctrl+C in this window.
echo.
python -m backend.app

pause
