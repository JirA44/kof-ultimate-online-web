@echo off
title BUG HUNTER 24/7 - KOF Ultimate Online
color 0A

echo.
echo ========================================
echo   BUG HUNTER 24/7 - Tests Permanents
echo ========================================
echo.
echo Ce script va lancer des IA qui jouent
echo en permanence pour detecter TOUS les bugs
echo.
echo Objectif: Passer de 2/20 a 18+/20
echo.
pause

cd /d "%~dp0"

:LOOP
echo.
echo [%date% %time%] Lancement nouveau cycle de tests...
echo.

python AI_PERMANENT_BUG_HUNTER.py

echo.
echo Cycle termine. Score genere dans BUG_REPORTS/
echo Relance dans 10 secondes...
echo.
timeout /t 10

goto LOOP
