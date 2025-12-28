@echo off
title KOF Ultimate Online - Launcher Pro
cd /d "%~dp0"
python KOF_ULTIMATE_PRO_LAUNCHER.py
if errorlevel 1 (
    echo.
    echo Python non trouve! Installation de secours...
    start "" "KOF_ONLINE_FIREBASE.html"
    start "" "Ikemen_GO.exe"
)
pause
