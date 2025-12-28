--[[
KOF ULTIMATE ONLINE - Custom Online Module
Opens Firebase lobby when "Online" is selected from main menu
Includes: Matchmaking, Profile, Rankings
]]--

local kof_online = {}

-- Path to our Firebase lobby
local LOBBY_PATH = "KOF_ONLINE_FIREBASE.html"

-- Function to open URL in default browser
local function openBrowser(path)
    local os_name = package.config:sub(1,1)
    local cmd
    if os_name == "\\" then
        -- Windows
        cmd = 'start "" "' .. path .. '"'
    else
        -- Linux/Mac
        cmd = 'xdg-open "' .. path .. '" 2>/dev/null || open "' .. path .. '"'
    end
    os.execute(cmd)
end

-- Function to override menu items (called after main is loaded)
local function setupMenuOverrides()
    if main == nil or main.t_itemname == nil then
        return false
    end

    -- Override serverhost (Host Game) to open our lobby
    main.t_itemname['serverhost'] = function(t, item)
        openBrowser(LOBBY_PATH)
        return nil  -- Stay on menu
    end

    -- Override netplayversus to show our lobby
    main.t_itemname['netplayversus'] = function(t, item)
        openBrowser(LOBBY_PATH)
        return nil
    end

    main.t_itemname['netplayteamcoop'] = function(t, item)
        openBrowser(LOBBY_PATH)
        return nil
    end

    main.t_itemname['netplaysurvivalcoop'] = function(t, item)
        openBrowser(LOBBY_PATH)
        return nil
    end

    -- Add custom menu items for KOF Online
    main.t_itemname['koflobby'] = function(t, item)
        openBrowser(LOBBY_PATH)
        return nil
    end

    main.t_itemname['kofprofile'] = function(t, item)
        openBrowser(LOBBY_PATH .. "#profile")
        return nil
    end

    main.t_itemname['kofrankings'] = function(t, item)
        openBrowser(LOBBY_PATH .. "#rankings")
        return nil
    end

    return true
end

-- Use hook to setup overrides when main is ready
hook.add("loop", "kof_online_setup", function()
    if not kof_online.initialized then
        if setupMenuOverrides() then
            kof_online.initialized = true
            print("[KOF Online] Menu overrides applied successfully")
        end
    end
end)

print("[KOF Online] Module loaded - Waiting for main menu...")

return kof_online
