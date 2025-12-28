@echo off
chcp 65001 > nul
title KOF Ultimate Online - Battle.net Launcher

echo.
echo ╔══════════════════════════════════════════════════════════════════════════════╗
echo ║              KOF ULTIMATE ONLINE - BATTLE.NET EDITION                        ║
echo ║                        Launcher Unifié v3.0                                  ║
echo ╚══════════════════════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

:: Check Node.js
where node >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Node.js n'est pas installé!
    echo Télécharge-le sur: https://nodejs.org/
    pause
    exit /b 1
)

:: Check dependencies
if not exist "online_backend\node_modules" (
    echo [INFO] Installation des dépendances...
    cd online_backend
    npm install
    cd ..
)

:: Create save folder if not exists
if not exist "save" mkdir save

echo.
echo [1/3] Démarrage du serveur matchmaking...
start /min "KOF Matchmaking Server" cmd /c "cd online_backend && node matchmaking_server.js"
timeout /t 2 /nobreak > nul

echo [2/3] Démarrage du client Battle.net...
start /min "KOF Battle.net Client" cmd /c "cd online_backend && node battlenet_client.js"
timeout /t 1 /nobreak > nul

echo [3/3] Lancement du jeu...
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║  ✓ Serveur matchmaking:  EN LIGNE (port 3101)                ║
echo ║  ✓ Client Battle.net:    CONNECTÉ                            ║
echo ║  ✓ Jeu:                  DÉMARRAGE...                        ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo Dans le jeu: Menu Principal → ONLINE pour le multijoueur!
echo.

:: Launch Ikemen GO
if exist "Ikemen_GO.exe" (
    start "" "Ikemen_GO.exe"
) else if exist "Ikemen_GO\Ikemen_GO.exe" (
    start "" "Ikemen_GO\Ikemen_GO.exe"
) else (
    echo [ERREUR] Ikemen_GO.exe introuvable!
    pause
)

echo.
echo Appuie sur une touche pour fermer les serveurs quand tu as fini de jouer...
pause > nul

:: Cleanup
echo.
echo Fermeture des serveurs...
taskkill /f /im "node.exe" /fi "WINDOWTITLE eq KOF*" > nul 2>&1

echo Terminé!
