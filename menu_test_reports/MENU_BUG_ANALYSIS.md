# KOF Ultimate Online - Analyse des Bugs de Menu

**Date**: 2026-01-23 10:30:20

## Resume

- Items de menu: 24
- Handlers trouves: 11
- **BUGS: 17**
- Warnings: 0

## BUGS CRITIQUES

| Type | Item/Handler | Message |
|------|--------------|----------|
| MISSING_HANDLER | arcade | Menu item 'ARCADE' (arcade) has no handler 'arcade' |
| MISSING_HANDLER | versus | Menu item 'VS MODE' (versus) has no handler 'versus' |
| MISSING_HANDLER | teamarcade | Menu item 'TEAM ARCADE' (teamarcade) has no handler 'teamarcade' |
| MISSING_HANDLER | teamversus | Menu item 'TEAM VS' (teamversus) has no handler 'teamversus' |
| MISSING_HANDLER | teamcoop | Menu item 'TEAM CO-OP' (teamcoop) has no handler 'teamcoop' |
| MISSING_HANDLER | survival | Menu item 'SURVIVAL' (survival) has no handler 'survival' |
| MISSING_HANDLER | survivalcoop | Menu item 'SURVIVAL CO-OP' (survivalcoop) has no handler 'survivalcoop' |
| MISSING_HANDLER | training | Menu item 'TRAINING' (training) has no handler 'training' |
| MISSING_HANDLER | netplay | Menu item 'ONLINE' (netplay) has no handler 'netplay' |
| MISSING_HANDLER | netplay_serverhost | Menu item 'HOST GAME' (netplay_serverhost) has no handler 'serverhost' |
| MISSING_HANDLER | netplay_serverjoin | Menu item 'JOIN GAME' (netplay_serverjoin) has no handler 'serverjoin' |
| MISSING_HANDLER | netplay_netplayversus | Menu item 'VERSUS 2P' (netplay_netplayversus) has no handler 'netplayversus' |
| MISSING_HANDLER | netplay_netplayteamcoop | Menu item 'ARCADE CO-OP' (netplay_netplayteamcoop) has no handler 'netplayteamcoop' |
| MISSING_HANDLER | netplay_netplaysurvivalcoop | Menu item 'SURVIVAL CO-OP' (netplay_netplaysurvivalcoop) has no handler 'netplaysurvivalcoop' |
| MISSING_HANDLER | options | Menu item 'OPTIONS' (options) has no handler 'options' |
| MISSING_HANDLER | exit | Menu item 'EXIT' (exit) has no handler 'exit' |
| MISSING_HANDLER | watch | Menu item 'WATCH' (watch) has no handler 'watch' |

## Items de Menu

| Item | Display | Handler | Status |
|------|---------|---------|--------|
| arcade | ARCADE | arcade | MISSING |
| exit | EXIT | exit | MISSING |
| netplay | ONLINE | netplay | MISSING |
| netplay_back | BACK | back | MISSING |
| netplay_battlenet | BATTLENET | battlenet | OK |
| netplay_firebase | WEB LOBBY | firebase | OK |
| netplay_joinadd | NEW ADDRESS | joinadd | MISSING |
| netplay_lobby | LIVE LOBBY | lobby | OK |
| netplay_netplaysurvivalcoop | SURVIVAL CO-OP | netplaysurvivalcoop | MISSING |
| netplay_netplayteamcoop | ARCADE CO-OP | netplayteamcoop | MISSING |
| netplay_netplayversus | VERSUS 2P | netplayversus | MISSING |
| netplay_profile | MY PROFILE | profile | OK |
| netplay_rankings | LEADERBOARD | rankings | OK |
| netplay_serverhost | HOST GAME | serverhost | MISSING |
| netplay_serverjoin | JOIN GAME | serverjoin | MISSING |
| options | OPTIONS | options | MISSING |
| survival | SURVIVAL | survival | MISSING |
| survivalcoop | SURVIVAL CO-OP | survivalcoop | MISSING |
| teamarcade | TEAM ARCADE | teamarcade | MISSING |
| teamcoop | TEAM CO-OP | teamcoop | MISSING |
| teamversus | TEAM VS | teamversus | MISSING |
| training | TRAINING | training | MISSING |
| versus | VS MODE | versus | MISSING |
| watch | WATCH | watch | MISSING |

---
*Analyse statique sans lancement du jeu*
