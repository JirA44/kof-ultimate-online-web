# Online Versus Mode - Implementation Report

## Date: 2026-01-23

## Overview
Implementation of the **online_versus** mode that allows players to select an AI opponent from the LIVE LOBBY and launch a match against them.

## Flow
1. Player opens **ONLINE** menu -> **LIVE LOBBY**
2. Player selects **LOBBY JOUEURS** tab
3. Player selects a player from the list
4. Player clicks **COMBATTRE** (Fight)
5. Opponent info is saved to `save/current_opponent.json`
6. `live_lobby.nextAction` is set to "online_versus"
7. Lobby closes
8. Main menu handler detects `nextAction = "online_versus"`
9. `main.t_itemname['online_versus']()` is called
10. Player selects their character (P2 is auto-selected)
11. Match starts against AI with difficulty based on opponent's ELO

## Files Modified

### external/script/main.lua
- Added `main.t_itemname['online_versus']` handler (lines 3220-3265)
- Handler configuration:
  - `main.cpuSide[2] = true` - P2 is AI controlled
  - `main.selectMenu[2] = false` - P2 doesn't appear in character selection
  - `main.charparam.ai = true` - AI parameters enabled
  - AI level calculated from opponent's ELO: `aiLevel = floor(elo / 300)` clamped to 1-8
  - Reads opponent from `save/current_opponent.json`

### external/script/live_lobby_screen.lua
- Modified player challenge action (around line 960-976)
- When player clicks "COMBATTRE":
  - Saves opponent data to JSON: `{username, elo, aiLevel, isAI}`
  - Sets `nextAction = "online_versus"`
  - Closes lobby

## AI Difficulty Mapping
| ELO Range | AI Level |
|-----------|----------|
| 0-299     | 1        |
| 300-599   | 1        |
| 600-899   | 2        |
| 900-1199  | 3        |
| 1200-1499 | 4        |
| 1500-1799 | 5        |
| 1800-2099 | 6        |
| 2100-2399 | 7        |
| 2400+     | 8        |

## Technical Details

### Character Selection
- P1: Manual selection (normal select screen)
- P2: Auto-selected by `launchFight()` in `default.lua`
  - When `main.cpuSide[2] = true` and P2 has no selected characters
  - `start.lua` lines 1743-1800 handle auto-fill from `main.t_availableChars`

### Game Mode
- Uses `setGameMode('versus')` for compatibility with start.lua checks
- The custom config (cpuSide, selectMenu) distinguishes it from regular versus

### Opponent Data Format
```json
{
  "username": "AI_Player_Name",
  "elo": 1500,
  "aiLevel": 5,
  "isAI": true
}
```

## Testing Instructions
1. Launch the game
2. Go to ONLINE menu
3. Select LIVE LOBBY
4. Navigate to LOBBY JOUEURS
5. Select any player
6. Press A to select action
7. Choose COMBATTRE
8. Verify character select shows only P1
9. Select a character
10. Verify match starts against AI

## Status: IMPLEMENTED
- Handler created: YES
- Lobby integration: YES
- AI difficulty: YES
- Auto-selection P2: YES
- File I/O: YES
