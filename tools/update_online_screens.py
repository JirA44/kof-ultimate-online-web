#!/usr/bin/env python3
"""Update online screens with full functionality"""

import os

# Leaderboard screen with profiles and matchmaking
leaderboard_lua = '''-- ============================================================================
-- KOF ULTIMATE ONLINE - LEADERBOARD SCREEN (ENHANCED)
-- ============================================================================

leaderboard_screen = leaderboard_screen or {}

leaderboard_screen.active = false
leaderboard_screen.data = {}
leaderboard_screen.scrollOffset = 0
leaderboard_screen.maxVisible = 12
leaderboard_screen.selectedIndex = 1
leaderboard_screen.viewingProfile = false
leaderboard_screen.profileData = nil
leaderboard_screen.message = ""
leaderboard_screen.messageTimer = 0

function leaderboard_screen.loadData()
    local path = "save/leaderboard.json"
    local file = io.open(path, "r")
    if file then
        local content = file:read("*all")
        file:close()
        if content and content ~= "" then
            local success, data = pcall(json.decode, content)
            if success and data and data.rankings then
                leaderboard_screen.data = data.rankings
                return true
            end
        end
    end
    return false
end

function leaderboard_screen.getWinrate(wins, losses)
    local total = wins + losses
    if total > 0 then return math.floor((wins / total) * 100) end
    return 0
end

function leaderboard_screen.showMessage(msg)
    leaderboard_screen.message = msg
    leaderboard_screen.messageTimer = 90
end

function leaderboard_screen.getProfileText()
    local p = leaderboard_screen.profileData
    if not p then return "No profile data" end
    local lines = {}
    table.insert(lines, "")
    table.insert(lines, "============================================")
    table.insert(lines, "          PLAYER PROFILE")
    table.insert(lines, "============================================")
    table.insert(lines, "")
    table.insert(lines, string.format("  Username:    %s", p.username or "Unknown"))
    table.insert(lines, string.format("  Title:       %s", p.title or "Rookie"))
    table.insert(lines, string.format("  ELO Rating:  %d", p.elo or 1200))
    table.insert(lines, string.format("  Rank:        #%d", p.rank or 0))
    table.insert(lines, "")
    table.insert(lines, "--------------------------------------------")
    table.insert(lines, "  STATISTICS")
    table.insert(lines, "--------------------------------------------")
    table.insert(lines, string.format("  Wins:        %d", p.wins or 0))
    table.insert(lines, string.format("  Losses:      %d", p.losses or 0))
    table.insert(lines, string.format("  Winrate:     %d%%", leaderboard_screen.getWinrate(p.wins or 0, p.losses or 0)))
    table.insert(lines, string.format("  Total:       %d games", (p.wins or 0) + (p.losses or 0)))
    table.insert(lines, "")
    table.insert(lines, "--------------------------------------------")
    table.insert(lines, "  [A] CHALLENGE TO DUEL")
    table.insert(lines, "  [B] Add to Friends")
    table.insert(lines, "  [ESC] Return to Leaderboard")
    if leaderboard_screen.message ~= "" then
        table.insert(lines, "")
        table.insert(lines, "  >>> " .. leaderboard_screen.message .. " <<<")
    end
    table.insert(lines, "")
    return table.concat(lines, "\\n")
end

function leaderboard_screen.getDisplayText()
    if leaderboard_screen.viewingProfile then
        return leaderboard_screen.getProfileText()
    end
    local lines = {}
    table.insert(lines, "")
    table.insert(lines, "========================================================")
    table.insert(lines, "         KOF ULTIMATE ONLINE - WORLD RANKINGS")
    table.insert(lines, "========================================================")
    table.insert(lines, "")
    table.insert(lines, string.format("  Total Players: %d", #leaderboard_screen.data))
    table.insert(lines, "")
    table.insert(lines, string.format("%-4s %-16s %6s %10s %7s %6s", " RK", "PLAYER", "ELO", "W/L", "WIN%", "TITLE"))
    table.insert(lines, "--------------------------------------------------------")

    local startIdx = leaderboard_screen.scrollOffset + 1
    local endIdx = math.min(startIdx + leaderboard_screen.maxVisible - 1, #leaderboard_screen.data)

    for i = startIdx, endIdx do
        local p = leaderboard_screen.data[i]
        if p then
            local name = p.username or "Unknown"
            if #name > 14 then name = string.sub(name, 1, 13) .. "." end
            local title = p.title or "Rookie"
            if #title > 6 then title = string.sub(title, 1, 6) end
            local line = string.format("%-4s %-16s %6d %10s %7s %6s",
                "#" .. (p.rank or i), name, p.elo or 1200,
                string.format("%d/%d", p.wins or 0, p.losses or 0),
                string.format("%d%%", leaderboard_screen.getWinrate(p.wins or 0, p.losses or 0)), title)
            if i == leaderboard_screen.selectedIndex then
                line = ">" .. line .. "<"
            else
                line = " " .. line
            end
            table.insert(lines, line)
        end
    end

    table.insert(lines, "--------------------------------------------------------")
    table.insert(lines, "")
    table.insert(lines, "  [UP/DOWN] Navigate   [A] View Profile")
    table.insert(lines, "  [X] FIND MATCH       [Y] Challenge Selected")
    table.insert(lines, "  [ESC] Back")
    if leaderboard_screen.message ~= "" then
        table.insert(lines, "")
        table.insert(lines, "  >>> " .. leaderboard_screen.message .. " <<<")
    end
    table.insert(lines, "")
    return table.concat(lines, "\\n")
end

function leaderboard_screen.viewProfile(index)
    if leaderboard_screen.data[index] then
        leaderboard_screen.profileData = leaderboard_screen.data[index]
        leaderboard_screen.viewingProfile = true
        leaderboard_screen.message = ""
    end
end

function leaderboard_screen.closeProfile()
    leaderboard_screen.viewingProfile = false
    leaderboard_screen.profileData = nil
    leaderboard_screen.message = ""
end

function leaderboard_screen.challengePlayer(index)
    local p = leaderboard_screen.data[index]
    if p then
        local challenge = {type = "challenge", from = "LocalPlayer", to = p.username, to_elo = p.elo, timestamp = os.date("%Y-%m-%d %H:%M:%S")}
        local file = io.open("save/pending_challenge.json", "w")
        if file then file:write(json.encode(challenge)); file:close() end
        leaderboard_screen.showMessage("Challenge sent to " .. (p.username or "Unknown") .. "!")
        return true
    end
    return false
end

function leaderboard_screen.findMatch()
    local request = {type = "matchmaking", player = "LocalPlayer", mode = "ranked", timestamp = os.date("%Y-%m-%d %H:%M:%S")}
    local file = io.open("save/matchmaking_request.json", "w")
    if file then file:write(json.encode(request)); file:close() end
    leaderboard_screen.showMessage("Searching for opponent...")
    return true
end

function leaderboard_screen.handleInput(cmd)
    if not leaderboard_screen.active then return false end
    if leaderboard_screen.messageTimer > 0 then
        leaderboard_screen.messageTimer = leaderboard_screen.messageTimer - 1
        if leaderboard_screen.messageTimer <= 0 then leaderboard_screen.message = "" end
    end
    if leaderboard_screen.viewingProfile then
        if commandGetState(cmd, "a") then leaderboard_screen.challengePlayer(leaderboard_screen.selectedIndex); return true end
        if commandGetState(cmd, "s") or commandGetState(cmd, "b") or esc() then leaderboard_screen.closeProfile(); return true end
        return false
    end
    if commandGetState(cmd, "$U") then
        if leaderboard_screen.selectedIndex > 1 then
            leaderboard_screen.selectedIndex = leaderboard_screen.selectedIndex - 1
            if leaderboard_screen.selectedIndex <= leaderboard_screen.scrollOffset then
                leaderboard_screen.scrollOffset = math.max(0, leaderboard_screen.scrollOffset - 1)
            end
        end
        return true
    end
    if commandGetState(cmd, "$D") then
        if leaderboard_screen.selectedIndex < #leaderboard_screen.data then
            leaderboard_screen.selectedIndex = leaderboard_screen.selectedIndex + 1
            if leaderboard_screen.selectedIndex > leaderboard_screen.scrollOffset + leaderboard_screen.maxVisible then
                leaderboard_screen.scrollOffset = leaderboard_screen.scrollOffset + 1
            end
        end
        return true
    end
    if commandGetState(cmd, "a") then leaderboard_screen.viewProfile(leaderboard_screen.selectedIndex); return true end
    if commandGetState(cmd, "y") then leaderboard_screen.challengePlayer(leaderboard_screen.selectedIndex); return true end
    if commandGetState(cmd, "x") then leaderboard_screen.findMatch(); return true end
    if commandGetState(cmd, "s") or esc() then leaderboard_screen.close(); return true end
    return false
end

function leaderboard_screen.open()
    leaderboard_screen.loadData()
    leaderboard_screen.active = true
    leaderboard_screen.scrollOffset = 0
    leaderboard_screen.selectedIndex = 1
    leaderboard_screen.viewingProfile = false
    leaderboard_screen.message = ""
end

function leaderboard_screen.close()
    leaderboard_screen.active = false
    leaderboard_screen.viewingProfile = false
end

function leaderboard_screen.isActive()
    return leaderboard_screen.active
end

function leaderboard_screen.init()
    leaderboard_screen.loadData()
end

leaderboard_screen.init()
return leaderboard_screen
'''

# Live lobby with matchmaking and AI training
lobby_lua = '''-- ============================================================================
-- KOF ULTIMATE ONLINE - LIVE LOBBY (ENHANCED)
-- ============================================================================

live_lobby = live_lobby or {}

live_lobby.active = false
live_lobby.data = nil
live_lobby.lastUpdate = 0
live_lobby.updateInterval = 2
live_lobby.selectedOption = 1
live_lobby.message = ""
live_lobby.messageTimer = 0
live_lobby.inMatchmaking = false
live_lobby.matchmakingTimer = 0

live_lobby.menuOptions = {
    {name = "FIND RANKED MATCH", action = "ranked"},
    {name = "FIND CASUAL MATCH", action = "casual"},
    {name = "TRAIN VS AI BOT", action = "ai_training"},
    {name = "CREATE LOBBY", action = "create"},
    {name = "VIEW LEADERBOARD", action = "leaderboard"},
    {name = "BACK TO MENU", action = "back"}
}

function live_lobby.loadData()
    local path = "save/server_status.json"
    local file = io.open(path, "r")
    if file then
        local content = file:read("*all")
        file:close()
        if content and content ~= "" then
            local success, data = pcall(json.decode, content)
            if success and data then
                live_lobby.data = data
                return true
            end
        end
    end
    return false
end

function live_lobby.showMessage(msg)
    live_lobby.message = msg
    live_lobby.messageTimer = 90
end

function live_lobby.getDisplayText()
    local lines = {}
    local d = live_lobby.data

    table.insert(lines, "")
    table.insert(lines, "============================================")
    table.insert(lines, "    KOF ULTIMATE ONLINE - LIVE LOBBY")
    table.insert(lines, "============================================")
    table.insert(lines, "")

    if d then
        table.insert(lines, string.format("  ONLINE: %d   MATCHES: %d   QUEUE: %d/%d",
            d.players_online or 0, d.active_matches or 0, d.queue_ranked or 0, d.queue_casual or 0))
    else
        table.insert(lines, "  Connecting to server...")
    end
    table.insert(lines, "")

    -- Menu options
    table.insert(lines, "--------------------------------------------")
    table.insert(lines, "  MATCHMAKING")
    table.insert(lines, "--------------------------------------------")

    for i, opt in ipairs(live_lobby.menuOptions) do
        local prefix = "  "
        if i == live_lobby.selectedOption then
            prefix = "> "
        end
        table.insert(lines, prefix .. opt.name)
    end

    table.insert(lines, "")
    table.insert(lines, "--------------------------------------------")
    table.insert(lines, "  LIVE ACTIVITY")
    table.insert(lines, "--------------------------------------------")

    if d and d.recent_activity and #d.recent_activity > 0 then
        local count = math.min(5, #d.recent_activity)
        for i = #d.recent_activity - count + 1, #d.recent_activity do
            local a = d.recent_activity[i]
            if a then
                local msg = a.message or ""
                if #msg > 42 then msg = string.sub(msg, 1, 39) .. "..." end
                table.insert(lines, string.format("  %s %s", a.timestamp or "", msg))
            end
        end
    else
        table.insert(lines, "  No recent activity")
    end

    table.insert(lines, "")
    table.insert(lines, "--------------------------------------------")
    table.insert(lines, "  [UP/DOWN] Select   [A] Confirm   [ESC] Back")

    if live_lobby.message ~= "" then
        table.insert(lines, "")
        table.insert(lines, "  >>> " .. live_lobby.message .. " <<<")
    end

    if live_lobby.inMatchmaking then
        table.insert(lines, "")
        table.insert(lines, "  SEARCHING FOR OPPONENT... (" .. live_lobby.matchmakingTimer .. "s)")
    end

    table.insert(lines, "")
    return table.concat(lines, "\\n")
end

function live_lobby.executeAction(action)
    if action == "ranked" then
        live_lobby.inMatchmaking = true
        live_lobby.matchmakingTimer = 0
        local request = {type = "matchmaking", player = "LocalPlayer", mode = "ranked", timestamp = os.date("%Y-%m-%d %H:%M:%S")}
        local file = io.open("save/matchmaking_request.json", "w")
        if file then file:write(json.encode(request)); file:close() end
        live_lobby.showMessage("Searching for RANKED match...")
    elseif action == "casual" then
        live_lobby.inMatchmaking = true
        live_lobby.matchmakingTimer = 0
        local request = {type = "matchmaking", player = "LocalPlayer", mode = "casual", timestamp = os.date("%Y-%m-%d %H:%M:%S")}
        local file = io.open("save/matchmaking_request.json", "w")
        if file then file:write(json.encode(request)); file:close() end
        live_lobby.showMessage("Searching for CASUAL match...")
    elseif action == "ai_training" then
        local request = {type = "ai_training", player = "LocalPlayer", ai_level = "same_elo", timestamp = os.date("%Y-%m-%d %H:%M:%S")}
        local file = io.open("save/ai_training_request.json", "w")
        if file then file:write(json.encode(request)); file:close() end
        live_lobby.showMessage("Starting AI Training Mode...")
    elseif action == "create" then
        live_lobby.showMessage("Creating lobby...")
    elseif action == "leaderboard" then
        live_lobby.close()
        if leaderboard_screen then leaderboard_screen.open() end
    elseif action == "back" then
        live_lobby.close()
    end
end

function live_lobby.handleInput(cmd)
    if not live_lobby.active then return false end

    if live_lobby.messageTimer > 0 then
        live_lobby.messageTimer = live_lobby.messageTimer - 1
        if live_lobby.messageTimer <= 0 then live_lobby.message = "" end
    end

    if live_lobby.inMatchmaking then
        live_lobby.matchmakingTimer = live_lobby.matchmakingTimer + 1
        if commandGetState(cmd, "s") or esc() then
            live_lobby.inMatchmaking = false
            live_lobby.showMessage("Matchmaking cancelled")
            return true
        end
        return false
    end

    if commandGetState(cmd, "$U") then
        if live_lobby.selectedOption > 1 then
            live_lobby.selectedOption = live_lobby.selectedOption - 1
        end
        return true
    end

    if commandGetState(cmd, "$D") then
        if live_lobby.selectedOption < #live_lobby.menuOptions then
            live_lobby.selectedOption = live_lobby.selectedOption + 1
        end
        return true
    end

    if commandGetState(cmd, "a") then
        local opt = live_lobby.menuOptions[live_lobby.selectedOption]
        if opt then live_lobby.executeAction(opt.action) end
        return true
    end

    if commandGetState(cmd, "s") or esc() then
        live_lobby.close()
        return true
    end

    return false
end

function live_lobby.open()
    live_lobby.loadData()
    live_lobby.active = true
    live_lobby.selectedOption = 1
    live_lobby.message = ""
    live_lobby.inMatchmaking = false
end

function live_lobby.close()
    live_lobby.active = false
    live_lobby.inMatchmaking = false
end

function live_lobby.isActive()
    return live_lobby.active
end

function live_lobby.update()
    if not live_lobby.active then return end
    local now = os.time()
    if now - live_lobby.lastUpdate >= live_lobby.updateInterval then
        live_lobby.loadData()
        live_lobby.lastUpdate = now
    end
end

function live_lobby.init()
    live_lobby.loadData()
end

live_lobby.init()
return live_lobby
'''

# Write files
base_dir = r"D:\KOF Ultimate Online"

with open(os.path.join(base_dir, "external/script/leaderboard_screen.lua"), "w", encoding="utf-8") as f:
    f.write(leaderboard_lua)
print("Updated: leaderboard_screen.lua")

with open(os.path.join(base_dir, "external/script/live_lobby_screen.lua"), "w", encoding="utf-8") as f:
    f.write(lobby_lua)
print("Updated: live_lobby_screen.lua")

print("\nAll online screens updated with:")
print("- Clickable player profiles")
print("- FIND MATCH button (X key)")
print("- Challenge player button (Y key)")
print("- AI Training mode")
print("- Matchmaking status")
