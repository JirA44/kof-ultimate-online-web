@echo off
REM Lancer l'IA de réparation en arrière-plan de façon silencieuse

cd /d "%~dp0"

REM Lancer en fenêtre minimisée
start /MIN "AI Auto Repair 24/7" cmd /c "python AI_AUTO_REPAIR_SYSTEM.py --continuous --interval 60 2>&1 > ai_repair_silent.log"

echo ✅ Systeme IA de reparation lance en arriere-plan!
echo 📋 Log: ai_repair_silent.log
echo.
echo Pour l'arreter: Ctrl+C dans la fenetre "AI Auto Repair 24/7"
echo.
timeout /t 3 >nul
