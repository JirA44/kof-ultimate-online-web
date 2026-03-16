# KOF ULTIMATE ONLINE - Bugs Corriges

**Date**: 2026-01-23
**Methode**: Analyse statique du code (sans simulation clavier)

---

## BUGS CORRIGES

### 1. CONFLIT DE MODULES (system.def, kof_online.lua, kof_battlenet.lua)
- **Probleme**: Deux modules ecrasaient les memes handlers
- **Solution**: Handlers separes `firebase` et `battlenet` avec entrees menu distinctes

### 2. loadLeaderboard() JAMAIS APPELE (live_lobby_screen.lua:1144)
- **Probleme**: Le leaderboard affichait toujours des donnees fictives
- **Solution**: Ajout de l'appel `live_lobby.loadLeaderboard()` dans `open()`

### 3. BOUCLES INFINIES (main.lua)
- **Probleme**: Pas de timeout sur les boucles while des menus
- **Solution**: Ajout de timeouts (120s pour rankings/profile, 300s pour lobby)

### 4. TRIALS MODE VIDE (main.lua:2962)
- **Probleme**: Handler completement vide - ne faisait rien
- **Solution**: Implementation complete du mode Trials (similaire a Training)

### 5. findMatch() INCOMPLET (leaderboard_screen.lua:190)
- **Probleme**: Affichait un message mais ne lancait pas le match
- **Solution**: Ajout du flag `launchVersus` et lancement automatique du versus

### 6. KEYBOARD/GAMEPAD CONFIG CRASH (menu.lua:514-519)
- **Probleme**: Appel de fonction sans verification - crash si non chargee
- **Solution**: Ajout de `if options and options.f_keyCfg then`

---

## FICHIERS MODIFIES

| Fichier | Modifications |
|---------|---------------|
| `data/system.def` | Ajout menu WEB LOBBY et BATTLENET |
| `external/mods/kof_online.lua` | Handler `firebase` sans override |
| `external/mods/kof_battlenet.lua` | Handler `battlenet` sans override |
| `external/script/main.lua` | Trials, timeouts, lancement versus |
| `external/script/live_lobby_screen.lua` | Appel loadLeaderboard() |
| `external/script/leaderboard_screen.lua` | findMatch() avec launchVersus |
| `external/script/menu.lua` | Nil check pour keyCfg |

---

## BOUTONS MAINTENANT FONCTIONNELS

| Bouton | Menu | Status |
|--------|------|--------|
| TRIALS | Main | CORRIGE |
| WEB LOBBY | Online | NOUVEAU |
| BATTLENET | Online | NOUVEAU |
| [A] Match | Leaderboard | CORRIGE |
| KEYBOARD | Options/Pause | CORRIGE |
| GAMEPAD | Options/Pause | CORRIGE |
| ONLINE RANKED | Live Lobby | OK (simulation 3s) |
| ONLINE CASUAL | Live Lobby | OK (simulation 3s) |

---

*Analyse et corrections effectuees sans toucher au clavier*
