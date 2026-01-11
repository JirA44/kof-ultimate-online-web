-- ============================================================================
-- KOF ULTIMATE ONLINE - IN-GAME ONLINE SYSTEM
-- ============================================================================
-- Battle.net style online features integrated directly into IKEMEN-GO
-- Features: Player profiles, ELO rankings, leaderboards, match history
-- ============================================================================

online = online or {}

-- Paths
online.profilesDir = "save/profiles/"
online.leaderboardFile = "save/leaderboard.json"
online.currentPlayerFile = "save/current_player.json"

-- Default values
online.DEFAULT_ELO = 1200
online.K_FACTOR = 32

-- Current player data
online.currentPlayer = nil
online.leaderboard = {}
online.onlinePlayers = {}

-- ============================================================================
-- FILE I/O FUNCTIONS
-- ============================================================================

function online.fileExists(path)
    local f = io.open(path, "r")
    if f then
        f:close()
        return true
    end
    return false
end

function online.loadJSON(path)
    if not online.fileExists(path) then
        return nil
    end
    local f = io.open(path, "r"); if not f then return nil end; local content = f:read("*all"); f:close()
    if content and content ~= "" then
        local success, data = pcall(json.decode, content)
        if success then
            return data
        end
    end
    return nil
end

function online.saveJSON(path, data)
    local content = json.encode(data, {indent = 2})
    main.f_fileWrite(path, content)
end

-- ============================================================================
-- PLAYER PROFILE FUNCTIONS
-- ============================================================================

function online.createDefaultProfile(username)
    return {
        username = username,
        elo = online.DEFAULT_ELO,
        wins = 0,
        losses = 0,
        win_streak = 0,
        max_win_streak = 0,
        main_characters = {},
        match_history = {},
        created_at = os.date("%Y-%m-%dT%H:%M:%S"),
        last_online = os.date("%Y-%m-%dT%H:%M:%S"),
        title = "Rookie",
        country = "Unknown",
        total_matches = 0,
        total_rounds_won = 0,
        total_rounds_lost = 0,
        perfect_rounds = 0
    }
end

function online.loadProfile(username)
    local path = online.profilesDir .. username .. ".json"
    local profile = online.loadJSON(path)
    if profile then
        return profile
    end
    return online.createDefaultProfile(username)
end

function online.saveProfile(profile)
    local path = online.profilesDir .. profile.username .. ".json"
    profile.last_online = os.date("%Y-%m-%dT%H:%M:%S")
    online.saveJSON(path, profile)
end

function online.getTitleFromELO(elo)
    if elo >= 2400 then return "Grand Master"
    elseif elo >= 2200 then return "Master"
    elseif elo >= 2000 then return "Diamond"
    elseif elo >= 1800 then return "Platinum"
    elseif elo >= 1600 then return "Gold"
    elseif elo >= 1400 then return "Silver"
    elseif elo >= 1200 then return "Bronze"
    else return "Rookie"
    end
end

function online.getWinrate(profile)
    local total = profile.wins + profile.losses
    if total > 0 then
        return math.floor((profile.wins / total) * 100)
    end
    return 0
end

-- ============================================================================
-- ELO CALCULATION
-- ============================================================================

function online.expectedScore(eloA, eloB)
    return 1 / (1 + math.pow(10, (eloB - eloA) / 400))
end

function online.calculateNewELO(winnerELO, loserELO)
    local expectedWinner = online.expectedScore(winnerELO, loserELO)
    local expectedLoser = online.expectedScore(loserELO, winnerELO)

    local newWinnerELO = math.floor(winnerELO + online.K_FACTOR * (1 - expectedWinner))
    local newLoserELO = math.floor(loserELO + online.K_FACTOR * (0 - expectedLoser))

    -- Minimum ELO is 100
    newLoserELO = math.max(100, newLoserELO)

    return newWinnerELO, newLoserELO
end

-- ============================================================================
-- MATCH RECORDING
-- ============================================================================

function online.recordMatch(player1Name, player2Name, winnerName, p1Char, p2Char, p1Rounds, p2Rounds)
    local player1 = online.loadProfile(player1Name)
    local player2 = online.loadProfile(player2Name)

    local matchId = os.time() .. "_" .. math.random(1000, 9999)
    local timestamp = os.date("%Y-%m-%dT%H:%M:%S")

    local eloChangeP1, eloChangeP2
    local newP1ELO, newP2ELO

    if winnerName == player1Name then
        newP1ELO, newP2ELO = online.calculateNewELO(player1.elo, player2.elo)
        eloChangeP1 = newP1ELO - player1.elo
        eloChangeP2 = newP2ELO - player2.elo

        player1.wins = player1.wins + 1
        player1.win_streak = player1.win_streak + 1
        player1.max_win_streak = math.max(player1.max_win_streak, player1.win_streak)
        player2.losses = player2.losses + 1
        player2.win_streak = 0
    else
        newP2ELO, newP1ELO = online.calculateNewELO(player2.elo, player1.elo)
        eloChangeP1 = newP1ELO - player1.elo
        eloChangeP2 = newP2ELO - player2.elo

        player2.wins = player2.wins + 1
        player2.win_streak = player2.win_streak + 1
        player2.max_win_streak = math.max(player2.max_win_streak, player2.win_streak)
        player1.losses = player1.losses + 1
        player1.win_streak = 0
    end

    -- Update ELO
    player1.elo = newP1ELO
    player2.elo = newP2ELO

    -- Update stats
    player1.total_matches = player1.total_matches + 1
    player2.total_matches = player2.total_matches + 1
    player1.total_rounds_won = player1.total_rounds_won + p1Rounds
    player1.total_rounds_lost = player1.total_rounds_lost + p2Rounds
    player2.total_rounds_won = player2.total_rounds_won + p2Rounds
    player2.total_rounds_lost = player2.total_rounds_lost + p1Rounds

    -- Update main characters
    if p1Char and p1Char ~= "" then
        table.insert(player1.main_characters, p1Char)
        if #player1.main_characters > 5 then
            table.remove(player1.main_characters, 1)
        end
    end
    if p2Char and p2Char ~= "" then
        table.insert(player2.main_characters, p2Char)
        if #player2.main_characters > 5 then
            table.remove(player2.main_characters, 1)
        end
    end

    -- Update titles
    player1.title = online.getTitleFromELO(player1.elo)
    player2.title = online.getTitleFromELO(player2.elo)

    -- Add to match history
    local matchSummary1 = {
        match_id = matchId,
        opponent = player2Name,
        result = (winnerName == player1Name) and "WIN" or "LOSS",
        elo_change = eloChangeP1,
        my_char = p1Char,
        opp_char = p2Char,
        score = p1Rounds .. "-" .. p2Rounds,
        timestamp = timestamp
    }
    table.insert(player1.match_history, matchSummary1)
    if #player1.match_history > 50 then
        table.remove(player1.match_history, 1)
    end

    local matchSummary2 = {
        match_id = matchId,
        opponent = player1Name,
        result = (winnerName == player2Name) and "WIN" or "LOSS",
        elo_change = eloChangeP2,
        my_char = p2Char,
        opp_char = p1Char,
        score = p2Rounds .. "-" .. p1Rounds,
        timestamp = timestamp
    }
    table.insert(player2.match_history, matchSummary2)
    if #player2.match_history > 50 then
        table.remove(player2.match_history, 1)
    end

    -- Save profiles
    online.saveProfile(player1)
    online.saveProfile(player2)

    -- Update leaderboard
    online.updateLeaderboard()

    return {
        match_id = matchId,
        winner = winnerName,
        elo_change_p1 = eloChangeP1,
        elo_change_p2 = eloChangeP2
    }
end

-- ============================================================================
-- LEADERBOARD FUNCTIONS
-- ============================================================================

function online.updateLeaderboard()
    local profiles = {}

    -- This would need filesystem listing which is limited in Lua
    -- For now, we'll load from the saved leaderboard file
    local leaderboardData = online.loadJSON(online.leaderboardFile)
    if leaderboardData and leaderboardData.rankings then
        online.leaderboard = leaderboardData.rankings
    end
end

function online.getLeaderboard(topN)
    topN = topN or 20
    local result = {}
    for i = 1, math.min(topN, #online.leaderboard) do
        result[i] = online.leaderboard[i]
    end
    return result
end

function online.getPlayerRank(username)
    for i, player in ipairs(online.leaderboard) do
        if player.username == username then
            return i
        end
    end
    return -1
end

-- ============================================================================
-- CURRENT PLAYER MANAGEMENT
-- ============================================================================

function online.setCurrentPlayer(username)
    online.currentPlayer = online.loadProfile(username)
    online.saveJSON(online.currentPlayerFile, {username = username})
end

function online.getCurrentPlayer()
    if online.currentPlayer then
        return online.currentPlayer
    end

    local data = online.loadJSON(online.currentPlayerFile)
    if data and data.username then
        online.currentPlayer = online.loadProfile(data.username)
        return online.currentPlayer
    end

    return nil
end

-- ============================================================================
-- DISPLAY FUNCTIONS (for in-game UI)
-- ============================================================================

function online.formatProfileDisplay(profile)
    local rank = online.getPlayerRank(profile.username)
    local rankStr = (rank > 0) and ("#" .. rank) or "Unranked"

    return string.format(
        "%s | %s | ELO: %d | %dW/%dL (%d%%)",
        profile.username,
        profile.title,
        profile.elo,
        profile.wins,
        profile.losses,
        online.getWinrate(profile)
    )
end

function online.formatLeaderboardEntry(entry, rank)
    return string.format(
        "#%d  %-20s  ELO: %4d  %s  %dW/%dL",
        rank,
        entry.username or entry.name,
        entry.elo,
        entry.title or online.getTitleFromELO(entry.elo),
        entry.wins,
        entry.losses
    )
end

-- ============================================================================
-- INITIALIZATION
-- ============================================================================

function online.init()
    -- Create directories if needed
    os.execute('mkdir "save\\profiles" 2>nul')

    -- Load leaderboard
    online.updateLeaderboard()

    -- Load current player if exists
    online.getCurrentPlayer()

    print("[KOF Online] System initialized")
    print("[KOF Online] Leaderboard entries: " .. #online.leaderboard)

    if online.currentPlayer then
        print("[KOF Online] Current player: " .. online.currentPlayer.username)
    end
end

-- ============================================================================
-- HOOK INTO MATCH END
-- ============================================================================

-- This function should be called when a match ends
function online.onMatchEnd(p1Name, p2Name, winnerNum, p1Char, p2Char, p1Rounds, p2Rounds)
    local winnerName = (winnerNum == 1) and p1Name or p2Name

    print("[KOF Online] Recording match: " .. p1Name .. " vs " .. p2Name)
    print("[KOF Online] Winner: " .. winnerName)

    local result = online.recordMatch(p1Name, p2Name, winnerName, p1Char, p2Char, p1Rounds, p2Rounds)

    print("[KOF Online] ELO changes: P1=" .. result.elo_change_p1 .. ", P2=" .. result.elo_change_p2)

    return result
end

-- Initialize on load
online.init()

return online
