# KOF Ultimate Online - Configuration Complete
# Executez ce script en tant qu'administrateur

# Verifier les droits admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "Relancement en mode Administrateur..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

Clear-Host
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║         KOF ULTIMATE ONLINE - CONFIGURATION COMPLETE                 ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# 1. Configuration Pare-feu
Write-Host "[1/4] Configuration du Pare-feu Windows..." -ForegroundColor Yellow
Write-Host ""

# Supprimer anciennes regles
$oldRules = @("KOF Ultimate Online*", "Ikemen GO*")
foreach ($rule in $oldRules) {
    Get-NetFirewallRule -DisplayName $rule -ErrorAction SilentlyContinue | Remove-NetFirewallRule -ErrorAction SilentlyContinue
}

# Ajouter nouvelles regles
try {
    # Regles pour le programme
    New-NetFirewallRule -DisplayName "KOF Ultimate Online - Ikemen GO (IN)" -Direction Inbound -Program "D:\KOF Ultimate Online\Ikemen_GO.exe" -Action Allow -Profile Any -Enabled True | Out-Null
    New-NetFirewallRule -DisplayName "KOF Ultimate Online - Ikemen GO (OUT)" -Direction Outbound -Program "D:\KOF Ultimate Online\Ikemen_GO.exe" -Action Allow -Profile Any -Enabled True | Out-Null

    # Regles pour le port 7500
    New-NetFirewallRule -DisplayName "KOF Ultimate Online - Port 7500 TCP" -Direction Inbound -Protocol TCP -LocalPort 7500 -Action Allow -Profile Any -Enabled True | Out-Null
    New-NetFirewallRule -DisplayName "KOF Ultimate Online - Port 7500 UDP" -Direction Inbound -Protocol UDP -LocalPort 7500 -Action Allow -Profile Any -Enabled True | Out-Null

    # Port 7501 (backup)
    New-NetFirewallRule -DisplayName "KOF Ultimate Online - Port 7501 TCP" -Direction Inbound -Protocol TCP -LocalPort 7501 -Action Allow -Profile Any -Enabled True | Out-Null
    New-NetFirewallRule -DisplayName "KOF Ultimate Online - Port 7501 UDP" -Direction Inbound -Protocol UDP -LocalPort 7501 -Action Allow -Profile Any -Enabled True | Out-Null

    Write-Host "  [OK] Regles pare-feu ajoutees!" -ForegroundColor Green
} catch {
    Write-Host "  [ERREUR] $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# 2. Verification des ports
Write-Host "[2/4] Verification des ports..." -ForegroundColor Yellow
Write-Host ""

$port7500 = Get-NetTCPConnection -LocalPort 7500 -ErrorAction SilentlyContinue
if ($port7500) {
    Write-Host "  [!] Port 7500 utilise par: $($port7500.OwningProcess)" -ForegroundColor Yellow
} else {
    Write-Host "  [OK] Port 7500 disponible!" -ForegroundColor Green
}

$port7501 = Get-NetTCPConnection -LocalPort 7501 -ErrorAction SilentlyContinue
if ($port7501) {
    Write-Host "  [!] Port 7501 utilise" -ForegroundColor Yellow
} else {
    Write-Host "  [OK] Port 7501 disponible!" -ForegroundColor Green
}

Write-Host ""

# 3. Detection IP
Write-Host "[3/4] Detection des adresses IP..." -ForegroundColor Yellow
Write-Host ""

# IP Locale
$localIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notlike "*Loopback*" -and $_.IPAddress -notlike "169.*" } | Select-Object -First 1).IPAddress
Write-Host "  IP Locale:   $localIP" -ForegroundColor White

# IP Publique
try {
    $publicIP = (Invoke-WebRequest -Uri "https://ifconfig.me/ip" -UseBasicParsing -TimeoutSec 5).Content.Trim()
    Write-Host "  IP Publique: $publicIP" -ForegroundColor Green
} catch {
    $publicIP = "Non detectee"
    Write-Host "  IP Publique: Non detectee (verifiez whatismyip.com)" -ForegroundColor Yellow
}

Write-Host ""

# 4. Creation du lanceur
Write-Host "[4/4] Creation du lanceur..." -ForegroundColor Yellow
Write-Host ""

$launcherContent = @"
@echo off
chcp 65001 >nul
title KOF Ultimate Online
color 0A

echo.
echo ══════════════════════════════════════════════════════════════════════
echo                     KOF ULTIMATE ONLINE
echo ══════════════════════════════════════════════════════════════════════
echo.
echo   Votre IP Publique: $publicIP
echo   Votre IP Locale:   $localIP
echo   Port: 7500
echo.
echo ══════════════════════════════════════════════════════════════════════
echo.
echo   [1] HEBERGER - Vous invitez quelqu'un (donnez votre IP publique)
echo   [2] REJOINDRE - Quelqu'un vous invite (entrez son IP dans le jeu)
echo.
echo ══════════════════════════════════════════════════════════════════════
echo.
echo Lancement du jeu...
echo.

start "" "D:\KOF Ultimate Online\Ikemen_GO.exe"
exit
"@

$launcherContent | Out-File -FilePath "D:\KOF Ultimate Online\LANCER_ONLINE.bat" -Encoding ASCII
Write-Host "  [OK] Lanceur cree: LANCER_ONLINE.bat" -ForegroundColor Green

Write-Host ""
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                    CONFIGURATION TERMINEE!                            ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "  VOTRE IP PUBLIQUE: " -NoNewline
Write-Host "$publicIP" -ForegroundColor Cyan
Write-Host "  (Donnez cette IP a vos amis pour qu'ils vous rejoignent)"
Write-Host ""
Write-Host "  Pour jouer:" -ForegroundColor Yellow
Write-Host "    1. Double-cliquez sur: D:\KOF Ultimate Online\LANCER_ONLINE.bat"
Write-Host "    2. Dans le jeu: NETWORK > HOST GAME (heberger) ou JOIN GAME (rejoindre)"
Write-Host ""
Write-Host "══════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Demander si lancer le jeu
$response = Read-Host "Lancer le jeu maintenant? (O/N)"
if ($response -eq "O" -or $response -eq "o") {
    Write-Host ""
    Write-Host "Lancement de KOF Ultimate Online..." -ForegroundColor Cyan
    Start-Process "D:\KOF Ultimate Online\Ikemen_GO.exe"
}

Write-Host ""
Write-Host "Appuyez sur une touche pour fermer..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
