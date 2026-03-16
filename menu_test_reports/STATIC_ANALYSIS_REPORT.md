# KOF ULTIMATE ONLINE - Analyse Statique des Menus

**Date**: 2026-01-23
**Methode**: Analyse du code source (pas de simulation clavier)

---

## BUGS CORRIGES

### BUG #1: CONFLIT DE MODULES - CORRIGE

**Probleme initial**: Deux modules overridaient les MEMES handlers de menu.

**Solution appliquee**:
- `kof_online.lua` utilise maintenant le handler `firebase` (menu "WEB LOBBY")
- `kof_battlenet.lua` utilise maintenant le handler `battlenet` (menu "BATTLENET")
- Les handlers originaux (`serverhost`, `netplayversus`, etc.) ne sont plus ecrases
- Chaque systeme a sa propre entree de menu

**Fichiers modifies**:
- `data/system.def` - Ajout des entrees menu `netplay_firebase` et `netplay_battlenet`
- `external/mods/kof_online.lua` - Handler `firebase` au lieu d'overrides
- `external/mods/kof_battlenet.lua` - Handler `battlenet` au lieu d'overrides

---

### BUG #2: loadLeaderboard() JAMAIS APPELE - CORRIGE

**Fichier**: `external/script/live_lobby_screen.lua`
**Correction**: Ajout de `live_lobby.loadLeaderboard()` dans `live_lobby.open()`

---

### BUG #3: BOUCLES INFINIES POSSIBLES - CORRIGE

**Fichier**: `external/script/main.lua`
**Correction**: Ajout de timeouts de securite:
- `rankings`: 120 secondes max
- `profile`: 120 secondes max
- `lobby`: 300 secondes max (5 min car lobby actif)

---

## BUGS HISTORIQUES (Reference)

**Fichier**: `live_lobby_screen.lua`
**Lignes**: 766-793

```lua
function live_lobby.loadLeaderboard()
    local path = "save/leaderboard.json"
    -- ... code qui charge le leaderboard
end
-- MAIS cette fonction n'est JAMAIS appelee!
```

**Consequence**: Le leaderboard affiche toujours les donnees sample codees en dur.

**Solution**: Appeler `live_lobby.loadLeaderboard()` dans `live_lobby.open()`

---

### BUG #3: BOUCLE INFINIE POSSIBLE

**Fichier**: `main.lua`
**Lignes**: 3063-3084

```lua
while leaderboard_screen.isActive() do
    -- Pas de timeout!
    -- Si isActive() ne retourne jamais false, boucle infinie
end
```

**Solution**: Ajouter un timeout de securite (ex: 60 secondes max)

---

### BUG #4: FICHIERS HTML MANQUANTS POTENTIELS

Les modules essaient d'ouvrir ces fichiers:
- `KOF_ONLINE_FIREBASE.html` (kof_online.lua:10)
- `KOF_BATTLENET_LOBBY.html` (kof_battlenet.lua:25)

**Verification necessaire**: Ces fichiers existent-ils dans le dossier racine?

---

### BUG #5: FONTS HARDCODES

**Fichier**: `live_lobby_screen.lua`

```lua
font = "font/jg.fnt"
font = "font/f-6x9.fnt"
```

**Risque**: Si ces polices n'existent pas, crash silencieux de l'UI.

---

## STRUCTURE DES MENUS (ANALYSE)

### Menu Principal (main.lua)
| Option | Handler | Fonction | Status |
|--------|---------|----------|--------|
| ARCADE | `arcade` | Lance mode Arcade | OK |
| VS MODE | `versus` | Lance VS local | OK |
| TEAM ARCADE | `teamarcade` | Alias de arcade | OK |
| TEAM VS | `teamversus` | Alias de versus | OK |
| SURVIVAL | `survival` | Lance mode Survival | OK |
| SURVIVAL CO-OP | `survivalcoop` | Lance Survival coop | OK |
| TRAINING | `training` | Lance mode Training | OK |
| OPTIONS | `options` | Ouvre menu options | OK |
| RANDOMTEST | `randomtest` | Test IA automatique | OK |

### Menu Online (main.lua + mods)
| Option | Handler Original | Override par Mod? | Status |
|--------|------------------|-------------------|--------|
| RANKINGS | `rankings` | NON | OK |
| MY PROFILE | `profile` | NON | OK |
| LIVE LOBBY | `lobby` | NON | OK |
| HOST GAME | `serverhost` | OUI (conflit!) | BUG |
| JOIN GAME | `serverjoin` | OUI (battlenet) | BUG |
| NETPLAY VS | `netplayversus` | OUI (conflit!) | BUG |

---

## ORDRE DE CHARGEMENT DES MODULES

1. `main.lua` - Definit handlers originaux
2. `kof_online.lua` - Override via hook("loop")
3. `kof_battlenet.lua` - Override via hook("loop")

**Le dernier a s'executer (kof_battlenet) gagne!**

---

## RECOMMANDATIONS

### PRIORITE HAUTE (A faire maintenant)

1. **Desactiver un module redondant**:
   - Soit supprimer/renommer `kof_online.lua`
   - Soit supprimer/renommer `kof_battlenet.lua`
   - Garder UN SEUL systeme online

2. **Ajouter appel loadLeaderboard()**:
   Dans `live_lobby_screen.lua`, fonction `open()`:
   ```lua
   function live_lobby.open()
       live_lobby.loadLeaderboard()  -- AJOUTER CETTE LIGNE
       -- ... reste du code
   end
   ```

### PRIORITE MOYENNE

3. Ajouter timeout aux boucles while dans rankings/profile
4. Verifier existence des fichiers HTML avant ouverture
5. Verifier existence des fonts avant chargement

### PRIORITE BASSE

6. Documenter quel systeme online utiliser
7. Nettoyer le code duplique

---

## FICHIERS ANALYSES

- `D:/KOF Ultimate Online kofuo/external/script/main.lua`
- `D:/KOF Ultimate Online kofuo/external/script/menu.lua`
- `D:/KOF Ultimate Online kofuo/external/mods/kof_online.lua`
- `D:/KOF Ultimate Online kofuo/external/mods/kof_battlenet.lua`
- `D:/KOF Ultimate Online kofuo/external/script/live_lobby_screen.lua`
- `D:/KOF Ultimate Online kofuo/external/script/leaderboard_screen.lua`

---

*Analyse effectuee sans simulation clavier - Code source uniquement*
