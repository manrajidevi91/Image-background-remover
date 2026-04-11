@echo off
SET VENV_DIR=venv

REM Check if virtual environment exists
IF NOT EXIST %VENV_DIR% (
    echo [INFO] Creating virtual environment...
    python -m venv %VENV_DIR%
)

REM Activate the virtual environment
echo [INFO] Activating virtual environment...
call %VENV_DIR%\Scripts\activate

REM Install or update requirements
echo [INFO] Installing/Updating dependencies...
pip install --upgrade pip
pip install -r requirements.txt

REM Run the application
echo [INFO] Running Image Background Remover...
python app.py

echo.
echo [INFO] Done.
pause
