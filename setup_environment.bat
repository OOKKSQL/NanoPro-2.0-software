@echo off
REM Super-Resolution Microscopy Application Setup
REM Windows Development Environment Setup

title Super-Resolution Microscopy Setup

echo.
echo ========================================
echo  Super-Resolution Microscopy Setup
echo ========================================
echo.
echo This script will set up the development environment.
echo It will create a virtual environment and install all
echo required dependencies for Windows development.
echo.
echo Prerequisites:
echo - Python 3.10 installed (required for PySpin compatibility)
echo - Internet connection for downloading packages
echo.
echo Checking Python 3.10 installation...

REM Check if Python 3.10 is available via py launcher
py -3.10 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python 3.10 is not installed or not accessible!
    echo.
    echo This application requires Python 3.10 for PySpin compatibility.
    echo Please download and install Python 3.10 from:
    echo https://www.python.org/downloads/release/python-3100/
    echo.
    echo Make sure to check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)

echo Python 3.10 found! Starting setup...
echo.
pause

echo Running Python setup script with Python 3.10...
py -3.10 "%~dp0setup_environment.py"

if %errorlevel% neq 0 (
    echo.
    echo Setup encountered errors. Please check the output above.
    echo.
) else (
    echo.
    echo Setup completed successfully!
    echo.
    echo To start the application, double-click Launch_Application.bat.
    echo.
)

echo.
pause
