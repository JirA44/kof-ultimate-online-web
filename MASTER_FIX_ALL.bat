@echo off
title MASTER FIX - Passage de 2/20 a 18+/20
color 0E

echo.
echo ================================================
echo   MASTER FIX - KOF Ultimate Online
echo   Objectif: Rendre le jeu esport-ready
echo ================================================
echo.
echo Score actuel: 2/20
echo Score cible:  18+/20
echo.
echo Ce script va:
echo   1. Reparer le systeme multijoueur
echo   2. Corriger tous les portraits et icones
echo   3. Lancer les tests IA 24/7
echo   4. Generer un rapport de qualite complet
echo.
pause

cd /d "%~dp0"

echo.
echo [ETAPE 1/4] Reparation systeme multijoueur...
echo ================================================
python FIX_MULTIPLAYER.py
if errorlevel 1 (
    echo ERREUR lors de la reparation multijoueur
    pause
)

echo.
echo [ETAPE 2/4] Reparation portraits et icones...
echo ================================================
python FIX_PORTRAITS_AND_ICONS.py
if errorlevel 1 (
    echo ERREUR lors de la reparation portraits
    pause
)

echo.
echo [ETAPE 3/4] Test du systeme multijoueur...
echo ================================================
python TEST_MULTIPLAYER.py

echo.
echo [ETAPE 4/4] Lancement Bug Hunter initial...
echo ================================================
echo Execution d'un premier cycle de tests complet...
echo (Cela va prendre quelques minutes)
timeout /t 3
python AI_PERMANENT_BUG_HUNTER.py

echo.
echo ================================================
echo   REPARATIONS TERMINEES
echo ================================================
echo.
echo Fichiers crees:
echo   - FIX_MULTIPLAYER.py : Reparation multijoueur
echo   - FIX_PORTRAITS_AND_ICONS.py : Reparation visuels
echo   - AI_PERMANENT_BUG_HUNTER.py : Tests IA 24/7
echo   - QUALITY_DASHBOARD.html : Dashboard de suivi
echo   - LAUNCH_BUG_HUNTER_24_7.bat : Tests permanents
echo.
echo Rapports generes dans:
echo   - BUG_REPORTS/ : Rapports detailles des bugs
echo   - PORTRAIT_FIXES_REPORT.md : Corrections visuelles
echo.
echo.
echo PROCHAINES ETAPES:
echo   1. Ouvrir QUALITY_DASHBOARD.html pour voir le score
echo   2. Lancer LAUNCH_BUG_HUNTER_24_7.bat pour tests continus
echo   3. Consulter les rapports dans BUG_REPORTS/
echo.
echo ================================================
echo.

start "" "QUALITY_DASHBOARD.html"

echo.
echo Voulez-vous lancer les tests IA en permanence maintenant? (O/N)
set /p choice=Votre choix:

if /i "%choice%"=="O" (
    echo.
    echo Lancement Bug Hunter 24/7...
    start "" "LAUNCH_BUG_HUNTER_24_7.bat"
)

echo.
echo Termine!
pause
