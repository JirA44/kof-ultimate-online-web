-- ============================================================================
-- KOF ULTIMATE ONLINE - LEADERBOARD SCREEN
-- ============================================================================

leaderboard_screen = leaderboard_screen or {}

leaderboard_screen.active = false
leaderboard_screen.data = {}
leaderboard_screen.scrollOffset = 0
leaderboard_screen.maxVisible = 10
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

function leaderboard_screen.getDisplayText()
    if leaderboard_screen.viewingProfile then
        return leaderboard_screen.getProfileText()
    end

    local lines = {}
    table.insert(lines, "")
    table.insert(lines, "====================================================")
    table.insert(lines, "            CLASSEMENT MONDIAL")
    table.insert(lines, "====================================================")
    table.insert(lines, string.format("  Joueurs: %d", #leaderboard_screen.data))
    table.insert(lines, "")
    table.insert(lines, string.format("%-4s %-8s %-14s %5s %7s %5s", " RK", "TYPE", "JOUEUR", "ELO", "W/L", "WIN%"))
    table.insert(lines, "----------------------------------------------------")

    local startIdx = leaderboard_screen.scrollOffset + 1
    local endIdx = math.min(startIdx + leaderboard_screen.maxVisible - 1, #leaderboard_screen.data)

    for i = startIdx, endIdx do
        local p = leaderboard_screen.data[i]
        if p then
            local name = p.username or "Unknown"
            if #name > 12 then name = string.sub(name, 1, 11) .. "." end

            local typeTag = "[SIM]"
            if p.isBot == true then typeTag = "[BOT]" end

            local winrate = leaderboard_screen.getWinrate(p.wins or 0, p.losses or 0)
            local wl = string.format("%d/%d", p.wins or 0, p.losses or 0)

            local line = string.format("%-4s %-8s %-14s %5d %7s %4d%%",
                "#" .. (p.rank or i), typeTag, name, p.elo or 1200, wl, winrate)

            if i == leaderboard_screen.selectedIndex then
                line = ">" .. string.sub(line, 2) .. "<"
            end
            table.insert(lines, line)
        end
    end

    table.insert(lines, "----------------------------------------------------")
    if leaderboard_screen.scrollOffset > 0 then
        table.insert(lines, "              ^ HAUT ^")
    end
    if endIdx < #leaderboard_screen.data then
        table.insert(lines, "              v BAS v")
    end
    table.insert(lines, "")
    table.insert(lines, " [Z] Profil  [A] Match  [S] Defier  [X/ESC] Retour")

    if leaderboard_screen.message ~= "" then
        table.insert(lines, "")
        table.insert(lines, "  >>> " .. leaderboard_screen.message .. " <<<")
    end

    return table.concat(lines, "\n")
end

function leaderboard_screen.getProfileText()
    local p = leaderboard_screen.profileData
    if not p then return "Pas de profil" end

    local lines = {}
    table.insert(lines, "")
    table.insert(lines, "====================================================")
    table.insert(lines, "              PROFIL JOUEUR")
    table.insert(lines, "====================================================")
    table.insert(lines, "")
    table.insert(lines, string.format("  Nom:       %s", p.username or "???"))
    table.insert(lines, string.format("  Rang:      #%d", p.rank or 0))
    table.insert(lines, string.format("  ELO:       %d", p.elo or 1200))
    table.insert(lines, string.format("  Titre:     %s", p.title or "Rookie"))
    table.insert(lines, "")
    table.insert(lines, "----------------------------------------------------")
    table.insert(lines, "  STATISTIQUES")
    table.insert(lines, "----------------------------------------------------")
    table.insert(lines, string.format("  Victoires: %d", p.wins or 0))
    table.insert(lines, string.format("  Defaites:  %d", p.losses or 0))
    table.insert(lines, string.format("  Winrate:   %d%%", leaderboard_screen.getWinrate(p.wins or 0, p.losses or 0)))
    table.insert(lines, string.format("  Total:     %d matchs", (p.wins or 0) + (p.losses or 0)))
    table.insert(lines, "")
    table.insert(lines, "----------------------------------------------------")
    table.insert(lines, " [Z] Defier  [X] Ami  [ENTER/ESC] Retour")

    if leaderboard_screen.message ~= "" then
        table.insert(lines, "")
        table.insert(lines, "  >>> " .. leaderboard_screen.message .. " <<<")
    end

    return table.concat(lines, "\n")
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
        leaderboard_screen.showMessage("Defi envoye a " .. (p.username or "Bot") .. "!")
        return true
    end
    return false
end

function leaderboard_screen.addToFriends(index)
    local p = leaderboard_screen.data[index]
    if p then
        local friends = {}
        local file = io.open("save/friends.json", "r")
        if file then
            local content = file:read("*all"); file:close()
            if content ~= "" then
                local ok, data = pcall(json.decode, content)
                if ok and data then friends = data end
            end
        end
        for _, f in ipairs(friends) do
            if f.username == p.username then
                leaderboard_screen.showMessage(p.username .. " deja ami!")
                return false
            end
        end
        table.insert(friends, {username = p.username, elo = p.elo})
        file = io.open("save/friends.json", "w")
        if file then file:write(json.encode(friends)); file:close() end
        leaderboard_screen.showMessage(p.username .. " ajoute!")
        return true
    end
    return false
end

function leaderboard_screen.findMatch()
    if #leaderboard_screen.data == 0 then
        leaderboard_screen.showMessage("Aucun joueur!")
        return false
    end
    local opp = leaderboard_screen.data[math.random(1, #leaderboard_screen.data)]
    if opp then
        leaderboard_screen.showMessage("Match vs " .. (opp.username or "Bot") .. "!")
    end
    return true
end

function leaderboard_screen.handleInput(cmd)
    if not leaderboard_screen.active then return false end
    
    -- DEBUG: Log all button presses to file
    local dbg = io.open("save/leaderboard_debug.txt", "a")
    if dbg then
        if commandGetState(cmd, "a") then dbg:write(os.date() .. " BUTTON A (Z key) pressed
") end
        if commandGetState(cmd, "b") then dbg:write(os.date() .. " BUTTON B (X key) pressed
") end
        if commandGetState(cmd, "x") then dbg:write(os.date() .. " BUTTON X (A key) pressed
") end
        if commandGetState(cmd, "y") then dbg:write(os.date() .. " BUTTON Y (S key) pressed
") end
        if commandGetState(cmd, "s") then dbg:write(os.date() .. " BUTTON S (ENTER) pressed
") end
        dbg:close()
    end

    if leaderboard_screen.messageTimer > 0 then
        leaderboard_screen.messageTimer = leaderboard_screen.messageTimer - 1
        if leaderboard_screen.messageTimer <= 0 then leaderboard_screen.message = "" end
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

    if leaderboard_screen.viewingProfile then
        if commandGetState(cmd, "a") then leaderboard_screen.challengePlayer(leaderboard_screen.selectedIndex); return true end
        if commandGetState(cmd, "b") then leaderboard_screen.addToFriends(leaderboard_screen.selectedIndex); return true end
        if commandGetState(cmd, "s") or esc() then leaderboard_screen.closeProfile(); return true end
        return false
    end

    if commandGetState(cmd, "a") then leaderboard_screen.viewProfile(leaderboard_screen.selectedIndex); return true end
    if commandGetState(cmd, "x") then leaderboard_screen.findMatch(); return true end
    if commandGetState(cmd, "y") then leaderboard_screen.challengePlayer(leaderboard_screen.selectedIndex); return true end
    if commandGetState(cmd, "b") or commandGetState(cmd, "s") or esc() then leaderboard_screen.close(); return true end

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
    math.randomseed(os.time())
end

leaderboard_screen.init()
return leaderboard_screen
