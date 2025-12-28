@echo off
title AI AUTO REPAIR SYSTEM 24/7 - Surveillance Permanente
color 0A

echo ================================================================
echo     AI AUTO REPAIR SYSTEM - MODE 24/7
echo ================================================================
echo.
echo  Ce script lance le systeme de reparation automatique
echo  qui surveille et corrige TOUTES les erreurs en permanence.
echo.
echo  Configuration:
echo    - Scan toutes les 60 secondes
echo    - Detection automatique des erreurs
echo    - Reparation immediate
echo    - Log complet des actions
echo.
echo ================================================================
echo.
echo Appuyez sur une touche pour demarrer...
pause >nul

cls
echo ================================================================
echo  DEMARRAGE DU SYSTEME IA...
echo ================================================================
echo.

cd /d "%~dp0"
python AI_AUTO_REPAIR_SYSTEM.py --continuous --interval 60

echo.
echo ================================================================
echo  SYSTEME ARRETE
echo ================================================================
echo.
pause
