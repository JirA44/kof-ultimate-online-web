--[[
╔══════════════════════════════════════════════════════════════════════════════╗
║              KOF ULTIMATE ONLINE - BATTLE.NET STYLE MODULE                   ║
║                   In-Game Matchmaking & Lobby System                         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Features:                                                                   ║
║  • Quick Match - One click to find opponent                                  ║
║  • Lobbies - See available games                                             ║
║  • Create Game - Host your own lobby                                         ║
║  • Profile - ELO rating & stats                                              ║
║  • Leaderboard - Top players                                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
]]--

local battlenet = {}

-- ============================================================================
-- CONFIGURATION
-- ============================================================================
local SAVE_DIR = "save/"
local STATE_FILE = SAVE_DIR .. "online_state.json"
local LOBBIES_FILE = SAVE_DIR .. "lobbies.json"
local COMMAND_FILE = SAVE_DIR .. "online_command.json"
local PROFILE_FILE = SAVE_DIR .. "player_profile.json"

local REFRESH_INTERVAL = 30  -- Refresh state every 30 frames (~0.5 sec)
local frameCounter = 0

-- State
battlenet.state = {
    connected = false,
    playerId = nil,
    playerName = "Player",
    elo = 1000,
    inQueue = false,
    currentMatch = nil,
    lobbies = {},
    lobbiesCount = 0
}

battlenet.initialized = false
battlenet.menuActive = false

-- ============================================================================
-- FILE I/O HELPERS
-- ============================================================================
local function readJson(filepath)
    local file = io.open(filepath, "r")
    if file then
        local content = file:read("*all")
        file:close()
        if content and content ~= "" then
            local success, result = pcall(json.decode, content)
            if success then
                return result
            end
        end
    end
    return nil
end

local function writeJson(filepath, data)
    local file = io.open(filepath, "w")
    if file then
        file:write(json.encode(data))
        file:close()
        return true
    end
    return false
end

-- ============================================================================
-- COMMANDS TO BATTLENET CLIENT
-- ============================================================================
function battlenet.sendCommand(action, params)
    local cmd = { action = action }
    if params then
        for k, v in pairs(params) do
            cmd[k] = v
        end
    end
    writeJson(COMMAND_FILE, cmd)
end

function battlenet.quickMatch()
    print("[KOF Online] Quick Match requested")
    battlenet.sendCommand("quick_match")
end

function battlenet.cancelQueue()
    print("[KOF Online] Cancel queue")
    battlenet.sendCommand("cancel_queue")
end

function battlenet.createLobby(name)
    print("[KOF Online] Creating lobby: " .. (name or "My Game"))
    battlenet.sendCommand("create_lobby", { name = name })
end

function battlenet.joinLobby(lobbyId)
    print("[KOF Online] Joining lobby: " .. lobbyId)
    battlenet.sendCommand("join_lobby", { lobbyId = lobbyId })
end

function battlenet.refreshLobbies()
    battlenet.sendCommand("refresh_lobbies")
end

function battlenet.setPlayerName(name)
    battlenet.sendCommand("set_name", { name = name })
end

-- ============================================================================
-- STATE READING
-- ============================================================================
function battlenet.refreshState()
    -- Read online state
    local state = readJson(STATE_FILE)
    if state then
        battlenet.state.connected = state.connected or false
        battlenet.state.playerId = state.playerId
        battlenet.state.playerName = state.playerName or "Player"
        battlenet.state.elo = state.elo or 1000
        battlenet.state.inQueue = state.inQueue or false
        battlenet.state.currentMatch = state.currentMatch
        battlenet.state.lobbiesCount = state.lobbiesCount or 0
    end

    -- Read lobbies
    local lobbiesData = readJson(LOBBIES_FILE)
    if lobbiesData and lobbiesData.lobbies then
        battlenet.state.lobbies = lobbiesData.lobbies
    end
end

-- ============================================================================
-- MATCH HANDLING
-- ============================================================================
function battlenet.checkForMatch()
    if battlenet.state.currentMatch then
        local match = battlenet.state.currentMatch

        if match.hostIp and not match.isHost then
            -- We have opponent IP, connect!
            print("[KOF Online] Connecting to opponent: " .. match.hostIp)
            -- Use Ikemen's built-in netplay
            enterNetPlay(match.hostIp)
            return true
        elseif match.isHost then
            -- We are host, wait for connection
            print("[KOF Online] Hosting game, waiting for opponent...")
            enterNetPlay("")
            return true
        end
    end
    return false
end

-- ============================================================================
-- MENU INTEGRATION
-- ============================================================================
function battlenet.setupMenus()
    if main == nil or main.t_itemname == nil then
        return false
    end

    -- Override netplay menu items for Battle.net experience

    -- Quick Match
    main.t_itemname['serverhost'] = function(t, item)
        if battlenet.state.connected then
            if battlenet.state.inQueue then
                battlenet.cancelQueue()
            else
                battlenet.quickMatch()
            end
        else
            print("[KOF Online] Not connected to server!")
        end
        return nil  -- Stay on menu
    end

    -- Join Lobby / Browse Games
    main.t_itemname['serverjoin'] = function(t, item)
        if battlenet.state.connected then
            battlenet.refreshLobbies()
            -- TODO: Show lobby list overlay
            print("[KOF Online] Lobbies: " .. battlenet.state.lobbiesCount)
        end
        return nil
    end

    -- Netplay Versus - Quick Match
    main.t_itemname['netplayversus'] = function(t, item)
        if battlenet.state.connected then
            battlenet.quickMatch()
            -- Check for match
            if battlenet.checkForMatch() then
                main.txt_mainSelect:update({text = "Online Versus"})
                setGameMode('netplayversus')
                return start.f_selectMenu
            end
        else
            print("[KOF Online] Connecting to server...")
        end
        return nil
    end

    return true
end

-- ============================================================================
-- STATUS DISPLAY
-- ============================================================================
function battlenet.getStatusText()
    if not battlenet.state.connected then
        return "OFFLINE - Connecting..."
    elseif battlenet.state.inQueue then
        return "SEARCHING FOR OPPONENT..."
    elseif battlenet.state.currentMatch then
        return "MATCH FOUND! vs " .. (battlenet.state.currentMatch.opponent and battlenet.state.currentMatch.opponent.playerName or "Unknown")
    else
        return string.format("ONLINE | %s | ELO: %d | Players: %d",
            battlenet.state.playerName,
            battlenet.state.elo,
            battlenet.state.lobbiesCount)
    end
end

-- ============================================================================
-- MAIN LOOP HOOK
-- ============================================================================
hook.add("loop", "kof_battlenet_loop", function()
    frameCounter = frameCounter + 1

    -- Initialize menus once
    if not battlenet.initialized then
        if battlenet.setupMenus() then
            battlenet.initialized = true
            print("[KOF Online] Battle.net module initialized!")
        end
    end

    -- Periodic state refresh
    if frameCounter >= REFRESH_INTERVAL then
        frameCounter = 0
        battlenet.refreshState()

        -- Auto-connect if match found
        if battlenet.state.currentMatch and not battlenet.menuActive then
            battlenet.checkForMatch()
        end
    end
end)

-- ============================================================================
-- INITIALIZATION
-- ============================================================================
print("╔══════════════════════════════════════════════════════════╗")
print("║     KOF ULTIMATE ONLINE - BATTLE.NET MODULE LOADED       ║")
print("╚══════════════════════════════════════════════════════════╝")

-- Initial state load
battlenet.refreshState()

return battlenet
