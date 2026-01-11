@echo off
title KOF Stage Capture - Appuie F12 pour screenshot
color 0A

echo ============================================================
echo   KOF ULTIMATE ONLINE - CAPTURE RAPIDE DES STAGES
echo ============================================================
echo.
echo Instructions:
echo   1. Lance le jeu Ikemen_GO.exe
echo   2. Va dans VS Mode ou Options ^> Stage Select
echo   3. Pour chaque stage, appuie sur F12 (screenshot Windows)
echo   4. Les screenshots vont dans: C:\Users\%USERNAME%\Videos\Captures
echo.
echo OU utilise Win+Alt+PrtSc pour screenshot Game Bar
echo.
echo ============================================================
echo.
echo Appuie sur une touche quand tu as fini pour generer la galerie...
pause > nul

echo.
echo Generation de la galerie...
python "%~dp0GENERATE_GALLERY.py"
pause
