@echo off
chcp 65001 > nul
title KOF Ultimate Online - Installer
color 0A

echo.
echo  ╔══════════════════════════════════════════════════════════════════════════╗
echo  ║                    KOF ULTIMATE ONLINE                                    ║
echo  ║                   All-in-One Launcher                                     ║
echo  ╚══════════════════════════════════════════════════════════════════════════╝
echo.
echo  Checking Python...

python --version > nul 2>&1
if errorlevel 1 (
    echo  Python not found! Starting game directly...
    start "" "Ikemen_GO.exe"
    exit
)

echo  Starting launcher...
echo.

python KOF_LAUNCHER.py

pause
