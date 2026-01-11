-- ============================================================================
-- KOF ULTIMATE ONLINE - PROFILE SCREEN (GRAPHICAL UI)
-- ============================================================================

profile_screen = profile_screen or {}

profile_screen.active = false
profile_screen.data = nil
profile_screen.matchHistoryOffset = 0
profile_screen.maxHistoryVisible = 5
profile_screen.animTimer = 0

-- ============================================================================
-- GRAPHICS INITIALIZATION
-- ============================================================================

profile_screen.gfx = {}
profile_screen.gfxInitialized = false

function profile_screen.initGraphics()
    if profile_screen.gfxInitialized then return end

    -- Background
    profile_screen.gfx.bgOverlay = rect:create({
        x1 = 0, y1 = 0, x2 = 320, y2 = 240,
        r = 0, g = 10, b = 30, src = 200, dst = 56
    })

    -- Header
    profile_screen.gfx.headerBar = rect:create({
        x1 = 0, y1 = 0, x2 = 320, y2 = 50,
        r = 40, g = 80, b = 140, src = 220, dst = 36
    })

    -- Stats box
    profile_screen.gfx.statsBox = rect:create({
        x1 = 10, y1 = 55, x2 = 155, y2 = 145,
        r = 20, g = 40, b = 80, src = 200, dst = 56
    })

    -- History box
    profile_screen.gfx.historyBox = rect:create({
        x1 = 160, y1 = 55, x2 = 310, y2 = 200,
        r = 20, g = 40, b = 80, src = 200, dst = 56
    })

    -- ELO display box
    profile_screen.gfx.eloBox = rect:create({
        x1 = 10, y1 = 150, x2 = 155, y2 = 200,
        r = 30, g = 60, b = 100, src = 200, dst = 56
    })

    -- Footer
    profile_screen.gfx.footerBar = rect:create({
        x1 = 0, y1 = 210, x2 = 320, y2 = 240,
        r = 40, g = 80, b = 140, src = 220, dst = 36
    })

    -- Title
    profile_screen.gfx.title = text:create({
        font = "font/jg.fnt", bank = 0, align = 0,
        text = "MY PROFILE", x = 160, y = 5,
        scaleX = 2.0, scaleY = 2.0, r = 255, g = 220, b = 100
    })

    -- Username
    profile_screen.gfx.username = text:create({
        font = "font/jg.fnt", bank = 0, align = 0,
        text = "", x = 160, y = 28,
        scaleX = 1.6, scaleY = 1.6, r = 100, g = 255, b = 150
    })

    -- Stats labels
    profile_screen.gfx.statsTitle = text:create({
        font = "font/f-6x9.fnt", bank = 0, align = 0,
        text = "STATISTICS", x = 82, y = 58,
        scaleX = 1.2, scaleY = 1.2, r = 255, g = 200, b = 100
    })

    profile_screen.gfx.statsLines = {}
    for i = 1, 5 do
        profile_screen.gfx.statsLines[i] = text:create({
            font = "font/f-6x9.fnt", bank = 0, align = -1,
            text = "", x = 15, y = 70 + (i - 1) * 14,
            scaleX = 1.1, scaleY = 1.1, r = 255, g = 255, b = 255
        })
    end

    -- ELO display
    profile_screen.gfx.eloLabel = text:create({
        font = "font/f-6x9.fnt", bank = 0, align = 0,
        text = "ELO RATING", x = 82, y = 153,
        scaleX = 1.0, scaleY = 1.0, r = 180, g = 180, b = 180
    })
    profile_screen.gfx.eloValue = text:create({
        font = "font/jg.fnt", bank = 0, align = 0,
        text = "", x = 82, y = 168,
        scaleX = 2.5, scaleY = 2.5, r = 255, g = 215, b = 0
    })
    profile_screen.gfx.tierName = text:create({
        font = "font/f-6x9.fnt", bank = 0, align = 0,
        text = "", x = 82, y = 190,
        scaleX = 1.2, scaleY = 1.2, r = 255, g = 255, b = 255
    })

    -- History
    profile_screen.gfx.historyTitle = text:create({
        font = "font/f-6x9.fnt", bank = 0, align = 0,
        text = "RECENT MATCHES", x = 235, y = 58,
        scaleX = 1.1, scaleY = 1.1, r = 255, g = 200, b = 100
    })

    profile_screen.gfx.historyLines = {}
    for i = 1, 6 do
        profile_screen.gfx.historyLines[i] = text:create({
            font = "font/f-6x9.fnt", bank = 0, align = -1,
            text = "", x = 165, y = 70 + (i - 1) * 20,
            scaleX = 1.0, scaleY = 1.0, r = 255, g = 255, b = 255
        })
    end

    -- Winrate bar
    profile_screen.gfx.winrateBarBg = rect:create({
        x1 = 15, y1 = 140, x2 = 150, y2 = 145,
        r = 60, g = 60, b = 60, src = 255, dst = 0
    })
    profile_screen.gfx.winrateBarFill = rect:create({
        x1 = 15, y1 = 140, x2 = 80, y2 = 145,
        r = 100, g = 255, b = 100, src = 255, dst = 0
    })

    -- Footer
    profile_screen.gfx.footer = text:create({
        font = "font/f-6x9.fnt", bank = 0, align = 0,
        text = "[HAUT/BAS] Historique  [ENTER/ESC] Retour", x = 160, y = 222,
        scaleX = 1.1, scaleY = 1.1, r = 200, g = 200, b = 200
    })

    profile_screen.gfxInitialized = true
end

-- ============================================================================
-- DATA FUNCTIONS
-- ============================================================================

function profile_screen.loadData(username)
    username = username or "LocalPlayer"
    local path = "save/profiles/" .. username .. ".json"
    local file = io.open(path, "r")
    if file then
        local content = file:read("*all")
        file:close()
        if content and content ~= "" then
            local success, data = pcall(json.decode, content)
            if success and data then
                profile_screen.data = data
                return true
            end
        end
    end

    profile_screen.data = {
        username = username, elo = 1200, wins = 0, losses = 0,
        win_streak = 0, max_win_streak = 0, title = "Rookie",
        total_matches = 0, match_history = {}
    }
    return true
end

function profile_screen.getTitleFromELO(elo)
    if elo >= 2400 then return "GRAND MASTER", 255, 50, 255 end
    if elo >= 2200 then return "MASTER", 255, 100, 100 end
    if elo >= 2000 then return "DIAMOND", 100, 200, 255 end
    if elo >= 1800 then return "PLATINUM", 200, 255, 200 end
    if elo >= 1600 then return "GOLD", 255, 215, 0 end
    if elo >= 1400 then return "SILVER", 192, 192, 192 end
    if elo >= 1200 then return "BRONZE", 205, 127, 50 end
    return "ROOKIE", 150, 150, 150
end

function profile_screen.getWinrate()
    if not profile_screen.data then return 0 end
    local total = profile_screen.data.wins + profile_screen.data.losses
    if total > 0 then return math.floor((profile_screen.data.wins / total) * 100) end
    return 0
end

function profile_screen.getRank()
    if not profile_screen.data then return -1 end
    local path = "save/leaderboard.json"
    local file = io.open(path, "r")
    if file then
        local content = file:read("*all")
        file:close()
        if content and content ~= "" then
            local success, data = pcall(json.decode, content)
            if success and data and data.rankings then
                for i, p in ipairs(data.rankings) do
                    if p.username == profile_screen.data.username then return i end
                end
            end
        end
    end
    return -1
end

-- ============================================================================
-- DRAWING
-- ============================================================================

function profile_screen.draw()
    if not profile_screen.active then return end

    profile_screen.initGraphics()
    profile_screen.animTimer = profile_screen.animTimer + 1

    local p = profile_screen.data
    if not p then return end

    -- Background
    profile_screen.gfx.bgOverlay:draw()
    profile_screen.gfx.headerBar:draw()
    profile_screen.gfx.statsBox:draw()
    profile_screen.gfx.historyBox:draw()
    profile_screen.gfx.eloBox:draw()
    profile_screen.gfx.footerBar:draw()

    -- Title with animation
    local pulse = math.abs(math.sin(profile_screen.animTimer * 0.05))
    profile_screen.gfx.title.r = 200 + math.floor(55 * pulse)
    profile_screen.gfx.title:draw()

    -- Username
    profile_screen.gfx.username.text = p.username or "Unknown"
    profile_screen.gfx.username:draw()

    -- Stats section
    profile_screen.gfx.statsTitle:draw()

    local rank = profile_screen.getRank()
    local rankStr = rank > 0 and "#" .. rank or "Unranked"
    local winrate = profile_screen.getWinrate()

    local stats = {
        string.format("Rank:    %s", rankStr),
        string.format("Wins:    %d", p.wins or 0),
        string.format("Losses:  %d", p.losses or 0),
        string.format("Winrate: %d%%", winrate),
        string.format("Streak:  %d (Max:%d)", p.win_streak or 0, p.max_win_streak or 0)
    }

    for i, stat in ipairs(stats) do
        local line = profile_screen.gfx.statsLines[i]
        if line then
            line.text = stat
            line:draw()
        end
    end

    -- Winrate bar
    profile_screen.gfx.winrateBarBg:draw()
    local barWidth = math.floor(135 * winrate / 100)
    profile_screen.gfx.winrateBarFill.x2 = 15 + barWidth
    if winrate >= 60 then
        profile_screen.gfx.winrateBarFill.r, profile_screen.gfx.winrateBarFill.g, profile_screen.gfx.winrateBarFill.b = 100, 255, 100
    elseif winrate >= 40 then
        profile_screen.gfx.winrateBarFill.r, profile_screen.gfx.winrateBarFill.g, profile_screen.gfx.winrateBarFill.b = 255, 255, 100
    else
        profile_screen.gfx.winrateBarFill.r, profile_screen.gfx.winrateBarFill.g, profile_screen.gfx.winrateBarFill.b = 255, 100, 100
    end
    profile_screen.gfx.winrateBarFill:draw()

    -- ELO display
    profile_screen.gfx.eloLabel:draw()
    profile_screen.gfx.eloValue.text = tostring(p.elo or 1200)
    local tierName, tr, tg, tb = profile_screen.getTitleFromELO(p.elo or 1200)
    profile_screen.gfx.eloValue.r, profile_screen.gfx.eloValue.g, profile_screen.gfx.eloValue.b = tr, tg, tb
    profile_screen.gfx.eloValue:draw()

    profile_screen.gfx.tierName.text = tierName
    profile_screen.gfx.tierName.r, profile_screen.gfx.tierName.g, profile_screen.gfx.tierName.b = tr, tg, tb
    profile_screen.gfx.tierName:draw()

    -- History section
    profile_screen.gfx.historyTitle:draw()

    if p.match_history and #p.match_history > 0 then
        local startIdx = math.max(1, #p.match_history - profile_screen.maxHistoryVisible - profile_screen.matchHistoryOffset + 1)
        local endIdx = math.min(#p.match_history, startIdx + profile_screen.maxHistoryVisible)

        local lineIdx = 1
        for i = endIdx, startIdx, -1 do
            local m = p.match_history[i]
            local line = profile_screen.gfx.historyLines[lineIdx]
            if m and line then
                local resultStr = m.result == "WIN" and "W" or "L"
                local eloStr = m.elo_change >= 0 and "+" .. m.elo_change or tostring(m.elo_change)
                local oppName = m.opponent or "???"
                if #oppName > 8 then oppName = string.sub(oppName, 1, 7) .. "." end

                line.text = string.format("%s %-8s %s", resultStr, oppName, eloStr)

                if m.result == "WIN" then
                    line.r, line.g, line.b = 100, 255, 100
                else
                    line.r, line.g, line.b = 255, 100, 100
                end
                line:draw()
                lineIdx = lineIdx + 1
            end
        end
    else
        profile_screen.gfx.historyLines[1].text = "No matches yet"
        profile_screen.gfx.historyLines[1].r, profile_screen.gfx.historyLines[1].g, profile_screen.gfx.historyLines[1].b = 150, 150, 150
        profile_screen.gfx.historyLines[1]:draw()
    end

    -- Footer
    profile_screen.gfx.footer:draw()
end

function profile_screen.getDisplayText()
    return "Use profile_screen.draw() for graphical UI"
end

-- ============================================================================
-- INPUT HANDLING
-- ============================================================================

function profile_screen.handleInput(cmd)
    if not profile_screen.active then return false end

    if commandGetState(cmd, "$U") then
        if profile_screen.matchHistoryOffset < (#(profile_screen.data.match_history or {}) - profile_screen.maxHistoryVisible) then
            profile_screen.matchHistoryOffset = profile_screen.matchHistoryOffset + 1
        end
        return true
    end

    if commandGetState(cmd, "$D") then
        if profile_screen.matchHistoryOffset > 0 then
            profile_screen.matchHistoryOffset = profile_screen.matchHistoryOffset - 1
        end
        return true
    end

    if commandGetState(cmd, "s") or esc() then
        profile_screen.close()
        return true
    end

    return false
end

-- ============================================================================
-- LIFECYCLE
-- ============================================================================

function profile_screen.open(username)
    profile_screen.loadData(username)
    profile_screen.active = true
    profile_screen.matchHistoryOffset = 0
    profile_screen.animTimer = 0
end

function profile_screen.close()
    profile_screen.active = false
end

function profile_screen.isActive()
    return profile_screen.active
end

function profile_screen.init()
    print("[Profile] Graphical screen initialized")
end

profile_screen.init()
return profile_screen
