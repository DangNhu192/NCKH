@echo off
title WEB SUPER v2.0 - Academic AI Platform
chcp 65001 >nul
cls

echo ========================================================
echo        🚀 WEB SUPER v2.0 - ACADEMIC RESEARCH AI
echo ========================================================
echo.
echo [*] Dang khoi dong Web Super Server...
echo.

cd /d "%~dp0"

REM 1. Uu tien dung moi truong Python ao .venv da cai dat day du 100%% thu vien
if exist ".venv\Scripts\python.exe" (
    echo [*] Phat hien moi truong .venv san sang. Dang chay server.py...
    ".venv\Scripts\python.exe" server.py
    goto :end
)

REM 2. Thu dung uv neu co
set "UV_CMD=uv"
if exist "%USERPROFILE%\.local\bin\uv.exe" set "UV_CMD=%USERPROFILE%\.local\bin\uv.exe"
if exist "C:\Users\User\.local\bin\uv.exe" set "UV_CMD=C:\Users\User\.local\bin\uv.exe"

"%UV_CMD%" run python server.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [*] Thu chay bang python he thong...
    python server.py
)

:end
pause
