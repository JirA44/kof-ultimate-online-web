@echo off
title KOF ULTIMATE - SYSTÈME AUTO-GUÉRISON AUTONOME
color 0B

echo ===============================================================
echo  🤖 SYSTÈME AUTONOME D'AUTO-GUÉRISON
echo  KOF ULTIMATE ONLINE
echo ===============================================================
echo.
echo  ⚡ LE JEU VA SE RÉPARER TOUT SEUL EN PERMANENCE
echo.
echo  Ce système effectue des cycles continus de:
echo  1. 🔍 Tests automatiques (détection bugs)
echo  2. 📊 Analyse automatique (diagnostic)
echo  3. 🔧 Réparation automatique (correction)
echo  4. ✅ Validation automatique (vérification)
echo  5. 🚀 Amélioration continue (optimisation)
echo.
echo  Chaque cycle dure ~10 minutes
echo  Pause de 5 minutes entre chaque cycle
echo  Le système tourne EN PERMANENCE sans intervention
echo.
echo ===============================================================
echo.
echo 📋 Vérification des fichiers...

if not exist "AUTONOMOUS_GAME_HEALER.py" (
    echo ❌ Fichier AUTONOMOUS_GAME_HEALER.py manquant!
    pause
    exit /b 1
)

if not exist "AI_TESTERS_ADVANCED.py" (
    echo ❌ Fichier AI_TESTERS_ADVANCED.py manquant!
    pause
    exit /b 1
)

echo ✅ Fichiers OK
echo.
echo 🎯 OBJECTIF: Passer de 2/20 à 18+/20 (Qualité Esport)
echo.
echo ⏸️  Pour arrêter: Ctrl+C
echo 📄 Logs: AUTONOMOUS_HEALER.log
echo 📊 Santé du jeu: GAME_HEALTH.json
echo 📄 Rapports: AUTO_HEALING_REPORT_*.md
echo.
echo ===============================================================
echo.
echo 🚀 Démarrage système autonome...
echo.

REM Lancer en mode minimisé
start /MIN "Auto-Healing System" cmd /c "python AUTONOMOUS_GAME_HEALER.py 2>&1"

echo ✅ Système autonome lancé en arrière-plan!
echo.
echo 📊 Pour voir la progression:
echo    type AUTONOMOUS_HEALER.log
echo.
echo 🔍 Pour voir l'état actuel:
echo    type GAME_HEALTH.json
echo.
echo 📄 Les rapports sont générés automatiquement dans:
echo    AUTO_HEALING_REPORT_*.md
echo.
echo ⏰ Le système effectue un cycle toutes les 15 minutes
echo    Laissez-le tourner plusieurs heures pour des résultats optimaux!
echo.
echo Appuyez sur une touche pour voir les logs en direct...
pause >nul

cls
echo ===============================================================
echo  📄 LOGS EN TEMPS RÉEL - SYSTÈME AUTO-GUÉRISON
echo ===============================================================
echo.
echo Ctrl+C pour arrêter l'affichage (le système continue en arrière-plan)
echo.
echo ===============================================================
echo.

REM Suivre les logs en temps réel
powershell -Command "Get-Content AUTONOMOUS_HEALER.log -Wait -Tail 50"
