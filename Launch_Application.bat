@echo off
setlocal

pushd "%~dp0"
if errorlevel 1 (
    echo Could not open the application folder.
    pause
    exit /b 1
)

if not exist "venv\Scripts\python.exe" (
    echo The application has not been set up yet.
    echo Run setup_environment.bat first, then try again.
    pause
    popd
    exit /b 1
)

"venv\Scripts\python.exe" "UI\main.py"
set "APP_EXIT_CODE=%errorlevel%"
if not "%APP_EXIT_CODE%"=="0" (
    echo.
    echo The application could not start. Check the error above.
    pause
)

popd
exit /b %APP_EXIT_CODE%
