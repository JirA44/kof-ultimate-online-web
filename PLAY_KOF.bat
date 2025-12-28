@echo off
chcp 65001 > nul
title KOF Ultimate Online - Launcher
color 0A

:MENU
cls
echo.
echo  ======================================================================
echo                     KOF ULTIMATE ONLINE
echo                        148 Characters
echo  ======================================================================
echo.
echo   [1] JOUER LOCAL      (VS Mode, Arcade, Training)
echo   [2] JOUER EN LIGNE   (Matchmaking, Rooms, Rankings)
echo   [3] REPARER LE JEU   (Auto-fix bugs)
echo   [Q] QUITTER
echo.
set /p choice="  Votre choix: "

if "%choice%"=="1" goto PLAY
if "%choice%"=="2" goto ONLINE
if "%choice%"=="3" goto REPAIR
if /i "%choice%"=="q" exit
goto MENU

:PLAY
cls
echo   Lancement de KOF Ultimate Online...
start "" "Ikemen_GO.exe"
goto MENU

:ONLINE
cls
echo   Ouverture du Lobby Online...
start "" "KOF_ONLINE_FIREBASE.html"
timeout /t 2 > nul
goto MENU

:REPAIR
cls
echo   Reparation automatique en cours...
python AUTO_FIX_ALL.py
python DEEP_FIX_CHARS.py
echo   Reparation terminee!
pause
goto MENU
