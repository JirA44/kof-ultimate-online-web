# KOF Ultimate Online - Auto Test Report

**Date**: 2026-02-01 06:48:35
**Status**: FAIL

## Summary

| Metric | Value |
|--------|-------|
| Errors | 5 |
| Warnings | 4 |
| Characters | 120 |
| Stages | 5 |

## Menu Handlers

| Handler | Status |
|---------|--------|
| arcade | OK |
| versus | OK |
| teamarcade | OK |
| teamversus | OK |
| survival | OK |
| survivalcoop | OK |
| training | OK |
| trials | OK |
| options | OK |
| rankings | MISSING |
| profile | MISSING |
| lobby | MISSING |
| firebase | MISSING |
| battlenet | MISSING |
| demo | OK |
| randomtest | OK |

## Modules

| Module | Status |
|--------|--------|
| leaderboard_screen | ERROR |
| profile_screen | ERROR |
| live_lobby | ERROR |
| online_system | ERROR |

## Data Files

| File | Status | Size |
|------|--------|------|
| save/leaderboard.json | OK | 8887 |
| save/online_players.json | OK | 983 |
| save/match_history.json | OK | 9641 |
| save/config.json | OK | 4965 |
| save/stats.json | OK | 86 |

## Errors

- **missing_handler**: Handler rankings is missing or not a function
- **missing_handler**: Handler profile is missing or not a function
- **missing_handler**: Handler lobby is missing or not a function
- **missing_handler**: Handler firebase is missing or not a function
- **missing_handler**: Handler battlenet is missing or not a function

## Warnings

- **missing_module**: Module leaderboard_screen is not loaded
- **missing_module**: Module profile_screen is not loaded
- **missing_module**: Module live_lobby is not loaded
- **missing_module**: Module online_system is not loaded

---
*Test executed silently without keyboard interaction*
