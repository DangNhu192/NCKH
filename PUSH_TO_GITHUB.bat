@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================================
echo   🚀 WEB SUPER - ĐỒNG BỘ VÀ ĐẨY MÃ NGUỒN LÊN GITHUB
echo   Repository: https://github.com/DangNhu192/NCKH
echo ========================================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0PUSH_TO_GITHUB.ps1" %*
