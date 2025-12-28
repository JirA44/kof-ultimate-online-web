@echo off
chcp 65001 >nul
title KOF Ultimate Online - Matchmaking ELO
color 0B

echo.
echo ╔══════════════════════════════════════════════════════════════════════╗
echo ║          KOF ULTIMATE ONLINE - MATCHMAKING ELO SYSTEM                ║
echo ╚══════════════════════════════════════════════════════════════════════╝
echo.

echo [1] LANCER LE SERVEUR MATCHMAKING (pour heberger)
echo [2] REJOINDRE LE MATCHMAKING (client)
echo [3] VOIR LE CLASSEMENT
echo [4] LANCER LE JEU SEULEMENT
echo.

set /p choice=Choix (1-4):

if "%choice%"=="1" goto server
if "%choice%"=="2" goto client
if "%choice%"=="3" goto ranking
if "%choice%"=="4" goto game

:server
echo.
echo Lancement du serveur matchmaking sur port 7600...
echo (Gardez cette fenetre ouverte!)
echo.
start "" "D:\KOF Ultimate Online\Ikemen_GO.exe"
python "D:\KOF Ultimate Online\matchmaking_elo.py"
goto end

:client
echo.
python "D:\KOF Ultimate Online\matchmaking_elo.py" client
goto end

:ranking
echo.
python -c "import sys; sys.path.insert(0,'D:/KOF Ultimate Online'); from matchmaking_elo import DB, Elo; db=DB(); top=db.top(20); print('\n=== CLASSEMENT TOP 20 ===\n'); [print(f\"  {p['#']:2}. {p['e']} {p['name']}: {p['elo']} ELO ({p['w']}W/{p['l']}L) {p['wr']}%%\") for p in top]"
echo.
pause
goto end

:game
start "" "D:\KOF Ultimate Online\Ikemen_GO.exe"
goto end

:end
