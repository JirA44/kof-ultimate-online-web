@echo off
title KOF ULTIMATE - Testeurs IA Multi-Profils 24/7
color 0A

echo ===============================================================
echo  🤖 SYSTÈME DE TESTEURS IA AVANCÉS - KOF ULTIMATE ONLINE
echo ===============================================================
echo.
echo  Ce système lance plusieurs testeurs IA en parallèle pour
echo  détecter TOUS les bugs:
echo.
echo  ✓ CRASHER: Détecte crashs au démarrage
echo  ✓ EXPLORER: Teste tous personnages et stages
echo  ✓ STRESS_TESTER: Spam d'inputs intensifs
echo  ✓ RAGE_QUITTER: Tests exits rapides
echo.
echo  Les testeurs tourneront EN PERMANENCE en arrière-plan
echo  et généreront des rapports automatiques tous les 10 tests.
echo.
echo ===============================================================
echo.

echo 📋 Vérification installation...
if not exist "AI_TESTERS_ADVANCED.py" (
    echo ❌ Fichier AI_TESTERS_ADVANCED.py manquant!
    pause
    exit /b 1
)

if not exist "chars" (
    echo ❌ Dossier chars/ manquant!
    pause
    exit /b 1
)

if not exist "stages" (
    echo ❌ Dossier stages/ manquant!
    pause
    exit /b 1
)

echo ✅ Installation OK
echo.
echo 🚀 Lancement des testeurs IA...
echo.
echo ⏸️  Pour arrêter: Ctrl+C dans cette fenêtre
echo 📊 Rapports générés dans BUG_REPORTS/
echo 🗃️  Base de données: BUG_DATABASE.json
echo.
echo ===============================================================
echo.

REM Lancer les testeurs IA en mode minimisé
start /MIN "AI Testers" cmd /c "python AI_TESTERS_ADVANCED.py 2>&1 > ai_testers.log"

echo ✅ Testeurs IA lancés en arrière-plan!
echo.
echo 📄 Logs en temps réel: ai_testers.log
echo 📊 Rapports: BUG_REPORTS/
echo.
echo Appuyez sur une touche pour voir les logs en direct...
pause >nul

REM Afficher les logs
echo.
echo 📄 LOGS EN DIRECT (Ctrl+C pour arrêter):
echo ===============================================================
echo.
type ai_testers.log
echo.
echo.
echo Pour continuer à surveiller les logs:
echo   type ai_testers.log
echo.
pause
