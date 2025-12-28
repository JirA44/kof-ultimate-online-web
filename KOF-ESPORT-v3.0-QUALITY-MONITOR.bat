@echo off
chcp 65001 >nul
title KOF Ultimate Online - Esport Quality Monitor v3.0

:: Couleurs et style
color 0B

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║     KOF ULTIMATE ONLINE - ESPORT QUALITY MONITOR v3.0      ║
echo ║                 Système de Monitoring Qualité               ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

:MENU
echo.
echo ┌────────────────────────────────────────────────────────────┐
echo │                      MENU PRINCIPAL                        │
echo └────────────────────────────────────────────────────────────┘
echo.
echo  [1] 🎯 Ouvrir Dashboard Qualité (HTML)
echo  [2] 📊 Lancer Audit Qualité Complet
echo  [3] 🔄 Monitoring Continu (60s)
echo  [4] 🚀 Lancer Bug Hunter 24/7
echo  [5] 🌐 Tester Système Multijoueur
echo  [6] 🎨 Vérifier Portraits/Icônes
echo  [7] 📈 Voir Rapport JSON
echo  [8] ❌ Quitter
echo.
set /p choice="Votre choix (1-8): "

if "%choice%"=="1" goto DASHBOARD
if "%choice%"=="2" goto AUDIT
if "%choice%"=="3" goto CONTINUOUS
if "%choice%"=="4" goto BUGHUNTER
if "%choice%"=="5" goto MULTIPLAYER
if "%choice%"=="6" goto PORTRAITS
if "%choice%"=="7" goto REPORT
if "%choice%"=="8" goto END

echo.
echo ❌ Choix invalide!
timeout /t 2 >nul
cls
goto MENU

:DASHBOARD
echo.
echo 🎯 Ouverture du Dashboard Qualité...
start "" "ESPORT_QUALITY_DASHBOARD.html"
timeout /t 2 >nul
goto MENU

:AUDIT
echo.
echo ┌────────────────────────────────────────────────────────────┐
echo │              AUDIT QUALITÉ COMPLET EN COURS                │
echo └────────────────────────────────────────────────────────────┘
echo.
python ESPORT_QUALITY_MONITOR.py
echo.
echo ✅ Audit terminé!
echo.
pause
goto MENU

:CONTINUOUS
echo.
echo ┌────────────────────────────────────────────────────────────┐
echo │              MONITORING CONTINU ACTIVÉ                     │
echo │          Analyse toutes les 60 secondes                    │
echo │          Appuyez sur Ctrl+C pour arrêter                   │
echo └────────────────────────────────────────────────────────────┘
echo.
python ESPORT_QUALITY_MONITOR.py --continuous 60
goto MENU

:BUGHUNTER
echo.
echo ┌────────────────────────────────────────────────────────────┐
echo │              BUG HUNTER 24/7 - DÉMARRAGE                   │
echo │          Tests automatiques permanents                     │
echo └────────────────────────────────────────────────────────────┘
echo.
echo 🚀 Lancement des tests IA automatiques...
start /min "" python AUTO_TEST_MINI_WINDOWS.py
echo.
echo ✅ Bug Hunter lancé en arrière-plan!
echo 📊 Surveillez le dashboard pour voir les résultats
echo.
timeout /t 3 >nul
goto MENU

:MULTIPLAYER
echo.
echo ┌────────────────────────────────────────────────────────────┐
echo │           TEST SYSTÈME MULTIJOUEUR                         │
echo └────────────────────────────────────────────────────────────┘
echo.
echo 🌐 Vérification du système multijoueur...
echo.

if exist "matchmaking_server.py" (
    echo ✅ Serveur matchmaking: TROUVÉ
) else (
    echo ❌ Serveur matchmaking: MANQUANT
)

if exist "matchmaking_client.py" (
    echo ✅ Client matchmaking: TROUVÉ
) else (
    echo ❌ Client matchmaking: MANQUANT
)

if exist "data\mugen.cfg" (
    echo ✅ Configuration: TROUVÉE
) else (
    echo ❌ Configuration: MANQUANTE
)

echo.
echo 🚀 Voulez-vous lancer le serveur matchmaking? (O/N)
set /p launch_server=""

if /i "%launch_server%"=="O" (
    echo.
    echo 🌐 Démarrage serveur matchmaking...
    start /min "" python matchmaking_server.py
    echo ✅ Serveur lancé en arrière-plan!
    timeout /t 2 >nul
)

echo.
pause
goto MENU

:PORTRAITS
echo.
echo ┌────────────────────────────────────────────────────────────┐
echo │           VÉRIFICATION PORTRAITS ET ICÔNES                 │
echo └────────────────────────────────────────────────────────────┘
echo.
echo 🎨 Scan des portraits en cours...
echo.

set portrait_issues=0
set icon_issues=0

for /d %%D in (chars\*) do (
    if not exist "%%D\portrait.png" (
        if not exist "%%D\portrait.pcx" (
            echo ⚠️ Portrait manquant: %%~nxD
            set /a portrait_issues+=1
        )
    )
)

echo.
if %portrait_issues%==0 (
    echo ✅ Tous les portraits sont OK!
) else (
    echo ❌ %portrait_issues% portrait(s) manquant(s) ou corrompu(s)
)

echo.
pause
goto MENU

:REPORT
echo.
echo ┌────────────────────────────────────────────────────────────┐
echo │              RAPPORT QUALITÉ JSON                          │
echo └────────────────────────────────────────────────────────────┘
echo.

if exist "esport_quality_report.json" (
    echo 📄 Contenu du rapport:
    echo.
    type esport_quality_report.json
    echo.
    echo.
    echo 🌐 Voulez-vous ouvrir dans le navigateur? (O/N)
    set /p open_json=""
    if /i "%open_json%"=="O" (
        start "" "esport_quality_report.json"
    )
) else (
    echo ❌ Aucun rapport trouvé!
    echo 💡 Lancez d'abord un audit (option 2)
)

echo.
pause
goto MENU

:END
echo.
echo ┌────────────────────────────────────────────────────────────┐
echo │                    À BIENTÔT!                              │
echo │          KOF Ultimate Online - Esport Quality              │
echo └────────────────────────────────────────────────────────────┘
echo.
timeout /t 2 >nul
exit
