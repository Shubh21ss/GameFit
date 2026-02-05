@echo off
REM GameFit - Build EXE Script
REM This script creates a professional EXE from your Flask application

echo.
echo ========================================
echo   GameFit - Build Professional EXE
echo ========================================
echo.

REM Check if virtual environment is activated
if not exist "venv_new\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    echo Please make sure you're in the project directory
    pause
    exit /b 1
)

echo [1/4] Installing PyInstaller...
venv_new\Scripts\pip.exe install pyinstaller --quiet
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller
    pause
    exit /b 1
)

echo [2/4] Gathering dependencies...
REM Make sure all data is included
if not exist "templates" (
    echo ERROR: templates folder not found!
    pause
    exit /b 1
)

if not exist "data\gamefit.db" (
    echo ERROR: data\gamefit.db not found!
    echo Run: python -c "from app import init_database, migrate_csv_to_database; init_database(); migrate_csv_to_database()"
    pause
    exit /b 1
)

if not exist "static\images" (
    echo ERROR: static\images folder not found!
    pause
    exit /b 1
)

if not exist "static\game_details" (
    echo ERROR: static\game_details folder not found!
    pause
    exit /b 1
)

echo [3/4] Building executable...
venv_new\Scripts\pyinstaller.exe ^
    --onefile ^
    --windowed ^
    --name="GameFit" ^
    --icon static/icon.ico ^
    --add-data "templates;templates" ^
    --add-data "static;static" ^
    --add-data "data\gamefit.db;data" ^
    app.py

if errorlevel 1 (
    echo ERROR: PyInstaller build failed
    pause
    exit /b 1
)

echo [4/4] Cleaning up...
rmdir /s /q build
del GameFit.spec

echo.
echo ========================================
echo   SUCCESS!
echo ========================================
echo.
echo Your GameFit.exe has been created!
echo Location: dist\GameFit.exe
echo.
echo You can now:
echo 1. Run GameFit.exe directly
echo 2. Share it with others (no Python needed!)
echo 3. Create an installer with NSIS
echo.
pause
