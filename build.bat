@echo off
chcp 65001 >nul 2>&1
echo Attendance Management System - Build Script
echo ===========================================

echo.
echo 1. Checking dependencies...
python -c "import pyinstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
)

echo.
echo 2. Building executable...
cd dist-src
pyinstaller attendance_app.spec

echo.
echo 3. Verifying build...
if exist "dist\AttendanceManagementSystem" (
    echo SUCCESS: Executable created at dist\AttendanceManagementSystem\
    echo Assets are included via spec configuration
    if not exist "dist\AttendanceManagementSystem\output" mkdir "dist\AttendanceManagementSystem\output" >nul 2>&1
    if not exist "dist\AttendanceManagementSystem\output\reports" mkdir "dist\AttendanceManagementSystem\output\reports" >nul 2>&1
    
    echo.
    echo BUILD COMPLETE!
    echo Executable: dist\AttendanceManagementSystem\AttendanceManagementSystem.exe
    echo.
    echo Contents:
    if exist "dist\AttendanceManagementSystem\AttendanceManagementSystem.exe" (
        echo - AttendanceManagementSystem.exe
    )
    if exist "dist\AttendanceManagementSystem\assets" (
        echo - assets folder
    )
    if exist "dist\AttendanceManagementSystem\settings.json" (
        echo - settings.json
    )
) else (
    echo ERROR: Build failed - executable not found
)

echo.
pause