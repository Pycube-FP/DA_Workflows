@echo off
echo 🏥 Asset Usage & Rental Tracking System - Installation
echo ============================================================

echo.
echo 📦 Upgrading pip...
python -m pip install --upgrade pip

echo.
echo 📦 Installing dependencies...
python -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo ❌ Error installing dependencies. Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo ✅ Installation completed successfully!
echo.
echo 🚀 To start the system:
echo    python app.py
echo.
echo 📍 Access the system at: http://localhost:5000
echo 👤 Login with: admin / admin123
echo.

set /p start="🤔 Would you like to start the system now? (y/n): "
if /i "%start%"=="y" (
    echo.
    echo 🚀 Starting the system...
    python app.py
) else (
    echo.
    echo 👋 You can start the system later by running: python app.py
)

pause 