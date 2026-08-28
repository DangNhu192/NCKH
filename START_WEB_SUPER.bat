@echo off
title WEB SUPER v2.0 - Academic AI Platform
chcp 65001 >nul
cls

echo ========================================================
echo        🚀 WEB SUPER v2.0 - ACADEMIC RESEARCH AI
echo ========================================================
echo.
echo [*] Dang khoi dong Web Super Server tai cong 8080...
echo [*] Trinh duyet se tu dong mo tai: http://127.0.0.1:8080
echo.

cd /d "%~dp0"
start "" "http://127.0.0.1:8080"

REM Kiem tra uv
set "UV_CMD=uv"
if exist "%USERPROFILE%\.local\bin\uv.exe" set "UV_CMD=%USERPROFILE%\.local\bin\uv.exe"
if exist "C:\Users\User\.local\bin\uv.exe" set "UV_CMD=C:\Users\User\.local\bin\uv.exe"

"%UV_CMD%" run --no-project --with fastapi --with uvicorn --with python-multipart --with python-docx --with pypdf --with requests --with pyzotero --with python-dotenv --with google-auth --with pyjwt --with deep-translator --with beautifulsoup4 --with google-generativeai --with matplotlib python server.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [*] Thu chay truc tiep bang python...
    python server.py
)

pause
