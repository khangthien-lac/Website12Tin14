@echo off
title Tour Website Server
echo ========================================
echo    KHOI DONG WEBSITE DU LICH
echo ========================================
echo.
cd /d "%~dp0\backend"
timeout /t 2 >nul
start "" "http://localhost:5000"
python app.py
