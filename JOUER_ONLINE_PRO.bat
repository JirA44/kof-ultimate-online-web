@echo off
title KOF Ultimate Online - Mode Pro
cd /d "%~dp0"

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║         KOF ULTIMATE ONLINE - READY TO PLAY PRO             ║
echo ╠══════════════════════════════════════════════════════════════╣
echo ║  156 Personnages certifies - 25 Stages - Score: 83/100     ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo [1] Lancer le JEU (Solo/Local)
echo [2] Ouvrir le LOBBY ONLINE (Matchmaking)
echo [3] Les DEUX (Jeu + Lobby)
echo [4] Lancer les Tests QA
echo [5] Quitter
echo.

set /p choix="Votre choix: "

if "%choix%"=="1" goto GAME
if "%choix%"=="2" goto LOBBY
if "%choix%"=="3" goto BOTH
if "%choix%"=="4" goto QA
if "%choix%"=="5" exit

:GAME
echo.
echo Lancement du jeu...
start "" "Ikemen_GO.exe"
goto END

:LOBBY
echo.
echo Ouverture du lobby online...
start "" "KOF_ONLINE_FIREBASE.html"
goto END

:BOTH
echo.
echo Lancement du jeu + lobby...
start "" "Ikemen_GO.exe"
timeout /t 2 >nul
start "" "KOF_ONLINE_FIREBASE.html"
goto END

:QA
echo.
echo Lancement des tests QA...
python QA_PROFESSIONAL_TESTER.py
pause
goto END

:END
echo.
echo Bon jeu!
timeout /t 3 >nul
