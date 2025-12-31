@echo off
REM Build script for Windows platforms
REM Creates standalone executables for x64, x86, and arm64

echo ==================================================
echo UEFIReader Windows Build Script
echo ==================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    exit /b 1
)

REM Install PyInstaller if not already installed
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Detect architecture
set PROCESSOR_ARCHITECTURE=%PROCESSOR_ARCHITECTURE%
if "%PROCESSOR_ARCHITECTURE%"=="AMD64" (
    set BUILD_ARCH=x64
) else if "%PROCESSOR_ARCHITECTURE%"=="ARM64" (
    set BUILD_ARCH=arm64
) else (
    set BUILD_ARCH=x86
)

echo Building for Windows %BUILD_ARCH%...
echo.

REM Build the executable
python build.py --platform windows --arch %BUILD_ARCH%

echo.
echo ==================================================
echo Build Complete!
echo ==================================================
echo.
echo Executable location: dist\windows_%BUILD_ARCH%\uefireader.exe
echo.
echo To test:
echo   dist\windows_%BUILD_ARCH%\uefireader.exe
echo.

pause
