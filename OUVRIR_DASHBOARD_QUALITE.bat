@echo off
chcp 65001 >nul
title Ouverture Dashboard Qualité Esport

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║            KOF ULTIMATE ONLINE - DASHBOARD QUALITÉ          ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

:: Vérifier si le dashboard existe
if not exist "ESPORT_QUALITY_DASHBOARD.html" (
    echo ❌ Erreur: ESPORT_QUALITY_DASHBOARD.html introuvable!
    echo.
    pause
    exit /b 1
)

echo 📊 Génération du dernier rapport...
python ESPORT_QUALITY_MONITOR.py >nul 2>&1

echo.
echo ✅ Rapport généré!
echo.
echo 🌐 Ouverture du dashboard dans votre navigateur...
echo.

start "" "ESPORT_QUALITY_DASHBOARD.html"

timeout /t 2 >nul

echo ✅ Dashboard ouvert!
echo.
echo 💡 Conseils:
echo    - Le dashboard se met à jour automatiquement toutes les 5s
echo    - Cliquez sur "Actualiser" pour forcer une mise à jour
echo    - Utilisez les boutons d'action pour lancer les outils
echo.
echo 📖 Pour plus d'informations, consultez GUIDE_ESPORT_QUALITY_SYSTEM.md
echo.

timeout /t 5 >nul
