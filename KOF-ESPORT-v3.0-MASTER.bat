@echo off
chcp 65001 >nul
title KOF Ultimate Online - MASTER ESPORT SUITE v3.0

:: Couleurs et style
color 0B

:MAIN_MENU
cls
echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║                                                                    ║
echo ║         KOF ULTIMATE ONLINE - MASTER ESPORT SUITE v3.0             ║
echo ║                                                                    ║
echo ║              🏆 Système Complet de Qualité Esport 🏆                ║
echo ║                                                                    ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

echo ┌────────────────────────────────────────────────────────────────────┐
echo │                        MENU PRINCIPAL                              │
echo └────────────────────────────────────────────────────────────────────┘
echo.
echo  ┌─ 🎯 MONITORING ET DASHBOARD ─────────────────────────────────────┐
echo  │                                                                  │
echo  │  [1] 📊 Dashboard Qualité (Web Interactif)                       │
echo  │  [2] 🔍 Audit Qualité Complet                                    │
echo  │  [3] 🔄 Monitoring Continu (60s)                                 │
echo  │                                                                  │
echo  └──────────────────────────────────────────────────────────────────┘
echo.
echo  ┌─ 🔧 RÉPARATIONS AUTOMATIQUES ────────────────────────────────────┐
echo  │                                                                  │
echo  │  [4] 🚀 RÉPARATION AUTO COMPLÈTE (Tout Réparer!)                 │
echo  │  [5] 🎨 Réparer Portraits Uniquement                             │
echo  │  [6] 🌐 Réparer Multijoueur Uniquement                           │
echo  │                                                                  │
echo  └──────────────────────────────────────────────────────────────────┘
echo.
echo  ┌─ 🧪 TESTS ET DÉTECTION ──────────────────────────────────────────┐
echo  │                                                                  │
echo  │  [7] 🤖 Lancer Bug Hunter 24/7                                   │
echo  │  [8] ⚔️  Tester Matchmaking                                      │
echo  │  [9] 🎮 Lancer le Jeu                                            │
echo  │                                                                  │
echo  └──────────────────────────────────────────────────────────────────┘
echo.
echo  ┌─ 📚 AIDE ET DOCUMENTATION ───────────────────────────────────────┐
echo  │                                                                  │
echo  │  [G] 📖 Guide Complet du Système                                 │
echo  │  [R] 📄 Voir Rapport JSON                                        │
echo  │  [S] 🛑 Tout Arrêter                                             │
echo  │                                                                  │
echo  └──────────────────────────────────────────────────────────────────┘
echo.
echo  [X] ❌ Quitter
echo.
set /p choice="👉 Votre choix: "

if /i "%choice%"=="1" goto DASHBOARD
if /i "%choice%"=="2" goto AUDIT
if /i "%choice%"=="3" goto CONTINUOUS
if /i "%choice%"=="4" goto FIX_ALL
if /i "%choice%"=="5" goto FIX_PORTRAITS
if /i "%choice%"=="6" goto FIX_MULTIPLAYER
if /i "%choice%"=="7" goto BUG_HUNTER
if /i "%choice%"=="8" goto TEST_MATCHMAKING
if /i "%choice%"=="9" goto LAUNCH_GAME
if /i "%choice%"=="G" goto GUIDE
if /i "%choice%"=="R" goto REPORT
if /i "%choice%"=="S" goto STOP_ALL
if /i "%choice%"=="X" goto END

echo.
echo ❌ Choix invalide!
timeout /t 2 >nul
goto MAIN_MENU

:DASHBOARD
cls
echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║                    📊 DASHBOARD QUALITÉ                            ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.
echo 🔄 Génération du rapport en cours...
python ESPORT_QUALITY_MONITOR.py >nul 2>&1
echo ✅ Rapport généré!
echo.
echo 🌐 Ouverture du dashboard dans votre navigateur...
start "" "ESPORT_QUALITY_DASHBOARD.html"
echo.
echo ✅ Dashboard ouvert!
echo.
echo 💡 Le dashboard se met à jour automatiquement toutes les 5 secondes.
echo.
pause
goto MAIN_MENU

:AUDIT
cls
echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║                    🔍 AUDIT QUALITÉ COMPLET                        ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.
python ESPORT_QUALITY_MONITOR.py
echo.
pause
goto MAIN_MENU

:CONTINUOUS
cls
echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║                    🔄 MONITORING CONTINU                           ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.
echo ⚠️  Le monitoring va s'exécuter en continu toutes les 60 secondes.
echo    Appuyez sur Ctrl+C pour arrêter.
echo.
pause
python ESPORT_QUALITY_MONITOR.py --continuous 60
goto MAIN_MENU

:FIX_ALL
cls
echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║              🚀 RÉPARATION AUTOMATIQUE COMPLÈTE                    ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.
echo 🎯 Ce module va réparer AUTOMATIQUEMENT:
echo.
echo    ✅ Tous les portraits manquants (189 détectés)
echo    ✅ La configuration multijoueur
echo    ✅ Et relancer un audit complet
echo.
echo ⏱️  Durée estimée: 2-5 minutes
echo.
pause
echo.
python AUTO_FIX_ALL_ESPORT.py
echo.
pause
goto MAIN_MENU

:FIX_PORTRAITS
cls
echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║                  🎨 RÉPARATION DES PORTRAITS                       ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.
python AUTO_FIX_PORTRAITS.py
echo.
pause
goto MAIN_MENU

:FIX_MULTIPLAYER
cls
echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║              🌐 RÉPARATION SYSTÈME MULTIJOUEUR                     ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.
python AUTO_FIX_MULTIPLAYER.py
echo.
pause
goto MAIN_MENU

:BUG_HUNTER
cls
echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║                  🤖 BUG HUNTER 24/7                                ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.
echo 🚀 Lancement du Bug Hunter en arrière-plan...
echo.
echo    Le Bug Hunter va:
echo    ✓ Lancer le jeu automatiquement
echo    ✓ Jouer des matchs IA vs IA
echo    ✓ Détecter les bugs et crashs
echo    ✓ Sauvegarder les logs
echo    ✓ Répéter toutes les 3 minutes
echo.
start /min "" python AUTO_TEST_MINI_WINDOWS.py
echo.
echo ✅ Bug Hunter lancé en arrière-plan!
echo 📊 Surveillez le dashboard pour voir les résultats.
echo 📁 Logs dans le dossier: logs\
echo.
pause
goto MAIN_MENU

:TEST_MATCHMAKING
cls
echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║                  ⚔️  TEST MATCHMAKING                              ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.
echo 🌐 Options de test:
echo.
echo  [1] Lancer serveur matchmaking
echo  [2] Tester avec joueurs virtuels
echo  [3] Retour
echo.
set /p mm_choice="Choix: "

if "%mm_choice%"=="1" (
    echo.
    echo 🌐 Démarrage serveur matchmaking...
    start "" python matchmaking_server.py
    echo ✅ Serveur démarré!
    pause
)
if "%mm_choice%"=="2" (
    echo.
    echo 🤖 Lancement test avec joueurs virtuels...
    python TEST_MATCHMAKING_INTELLIGENT.py
    pause
)

goto MAIN_MENU

:LAUNCH_GAME
cls
echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║                      🎮 LANCEMENT DU JEU                           ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.
if exist "KOF_Ultimate_Online.exe" (
    echo 🚀 Lancement de KOF Ultimate Online...
    start "" "KOF_Ultimate_Online.exe"
    echo ✅ Jeu lancé!
) else (
    echo ❌ Erreur: KOF_Ultimate_Online.exe introuvable!
)
echo.
timeout /t 2 >nul
goto MAIN_MENU

:GUIDE
cls
echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║                  📖 GUIDE COMPLET DU SYSTÈME                       ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.
if exist "GUIDE_ESPORT_QUALITY_SYSTEM.md" (
    echo 📄 Ouverture du guide...
    start "" "GUIDE_ESPORT_QUALITY_SYSTEM.md"
    echo ✅ Guide ouvert!
) else (
    echo ❌ Guide introuvable!
)
echo.
timeout /t 2 >nul
goto MAIN_MENU

:REPORT
cls
echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║                    📄 RAPPORT JSON                                 ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.
if exist "esport_quality_report.json" (
    echo 📊 Contenu du rapport:
    echo.
    type esport_quality_report.json
    echo.
) else (
    echo ❌ Aucun rapport trouvé!
    echo 💡 Lancez d'abord un audit (option 2)
)
echo.
pause
goto MAIN_MENU

:STOP_ALL
cls
echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║                      🛑 ARRÊT DE TOUT                              ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.
echo 🛑 Arrêt de tous les processus en cours...
echo.
taskkill /F /IM python.exe /FI "WINDOWTITLE eq AUTO_TEST*" >nul 2>&1
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *matchmaking*" >nul 2>&1
echo.
echo ✅ Tous les processus arrêtés!
echo.
timeout /t 2 >nul
goto MAIN_MENU

:END
cls
echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║                                                                    ║
echo ║                         À BIENTÔT!                                 ║
echo ║                                                                    ║
echo ║              🏆 KOF Ultimate Online - Esport Ready 🏆               ║
echo ║                                                                    ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.
timeout /t 3 >nul
exit
