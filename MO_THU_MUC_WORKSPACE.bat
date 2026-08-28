@echo off
chcp 65001 > nul
echo =======================================================
echo     ĐANG MỞ THƯ MỤC WORKSPACE CỦA WEB SUPER...
echo =======================================================
cd /d "%~dp0"
explorer.exe /root,"%~dp0workspace"
