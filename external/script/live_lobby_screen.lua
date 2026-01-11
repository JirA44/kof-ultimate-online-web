-- ============================================================================
-- KOF ULTIMATE ONLINE - LIVE LOBBY (MODERN GRAPHICAL UI)
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

-- Mode d'affichage: "menu", "players", ou "player_action"
live_lobby.viewMode = "menu"
live_lobby.selectedPlayer = 1
live_lobby.onlinePlayers = {}
live_lobby.filteredPlayers = {}

-- Mode action sur joueur (submenu Defier Oui/Non)
live_lobby.playerActionMode = false
live_lobby.playerActionOption = 1  -- 1 = DEFIER, 2 = PROFIL, 3 = ANNULER
live_lobby.selectedPlayerData = nil

-- Recherche de joueur
live_lobby.searchMode = false
live_lobby.searchText = ""

-- Systeme de defi
live_lobby.pendingChallenge = nil
live_lobby.challengeTimer = 0
live_lobby.challengeSent = false
live_lobby.challengeTarget = nil

-- Action a executer apres fermeture du lobby
live_lobby.nextAction = nil

-- Animation timer
live_lobby.animTimer = 0

live_lobby.menuOptions = {
    {name = "MATCH CLASSE", action = "ranked", icon = "!"},
    {name = "MATCH CASUAL", action = "casual", icon = "*"},
    {name = "JOUEURS EN LIGNE", action = "players", icon = "@"},
    {name = "ENTRAINEMENT IA", action = "ai_training", icon = "#"},
    {name = "CREER LOBBY", action = "create", icon = "+"},
    {name = "CLASSEMENT", action = "leaderboard", icon = "="},
    {name = "RETOUR AU MENU", action = "back", icon = "<"}
}

-- ============================================================================
-- GRAPHICAL UI ELEMENTS
-- ============================================================================

live_lobby.gfx = {}
live_lobby.gfxInitialized = false

function live_lobby.initGraphics()
    if live_lobby.gfxInitialized then return end

    -- Main title - BIG
    live_lobby.gfx.title = text:create({
        font = "font/jg.fnt",
        bank = 0,
        align = 0,
        text = "KOF ULTIMATE ONLINE",
        x = 160,
        y = 15,
        scaleX = 2.5,
        scaleY = 2.5,
        r = 255,
        g = 200,
        b = 50
    })

    -- Subtitle
    live_lobby.gfx.subtitle = text:create({
        font = "font/f-6x9.fnt",
        bank = 0,
        align = 0,
        text = "LIVE LOBBY",
        x = 160,
        y = 38,
        scaleX = 1.5,
        scaleY = 1.5,
        r = 200,
        g = 200,
        b = 255
    })

    -- Status bar text
    live_lobby.gfx.statusBar = text:create({
        font = "font/f-6x9.fnt",
        bank = 0,
        align = 0,
        text = "",
        x = 160,
        y = 52,
        scaleX = 1.2,
        scaleY = 1.2,
        r = 150,
        g = 255,
        b = 150
    })

    -- Menu items (7 items) - BIGGER TEXT
    live_lobby.gfx.menuItems = {}
    for i = 1, 7 do
        live_lobby.gfx.menuItems[i] = text:create({
            font = "font/jg.fnt",
            bank = 0,
            align = -1,
            text = "",
            x = 50,
            y = 70 + (i - 1) * 22,
            scaleX = 1.8,
            scaleY = 1.8,
            r = 255,
            g = 255,
            b = 255
        })
    end

    -- Selection cursor text
    live_lobby.gfx.cursor = text:create({
        font = "font/jg.fnt",
        bank = 0,
        align = -1,
        text = ">>",
        x = 25,
        y = 70,
        scaleX = 2.0,
        scaleY = 2.0,
        r = 255,
        g = 255,
        b = 0
    })

    -- Player list items (8 items)
    live_lobby.gfx.playerItems = {}
    for i = 1, 8 do
        live_lobby.gfx.playerItems[i] = text:create({
            font = "font/f-6x9.fnt",
            bank = 0,
            align = -1,
            text = "",
            x = 25,
            y = 65 + (i - 1) * 18,
            scaleX = 1.4,
            scaleY = 1.4,
            r = 255,
            g = 255,
            b = 255
        })
    end

    -- Section title
    live_lobby.gfx.sectionTitle = text:create({
        font = "font/jg.fnt",
        bank = 0,
        align = 0,
        text = "",
        x = 160,
        y = 55,
        scaleX = 1.6,
        scaleY = 1.6,
        r = 100,
        g = 200,
        b = 255
    })

    -- Footer / help text
    live_lobby.gfx.footer = text:create({
        font = "font/f-6x9.fnt",
        bank = 0,
        align = 0,
        text = "[Z] Confirmer  [X] Retour",
        x = 160,
        y = 225,
        scaleX = 1.2,
        scaleY = 1.2,
        r = 180,
        g = 180,
        b = 180
    })

    -- Message popup
    live_lobby.gfx.message = text:create({
        font = "font/jg.fnt",
        bank = 0,
        align = 0,
        text = "",
        x = 160,
        y = 205,
        scaleX = 1.4,
        scaleY = 1.4,
        r = 255,
        g = 255,
        b = 100
    })

    -- Challenge popup title
    live_lobby.gfx.challengeTitle = text:create({
        font = "font/jg.fnt",
        bank = 0,
        align = 0,
        text = "DEFI RECU!",
        x = 160,
        y = 80,
        scaleX = 2.2,
        scaleY = 2.2,
        r = 255,
        g = 50,
        b = 50
    })

    -- Challenge details
    live_lobby.gfx.challengeDetails = text:create({
        font = "font/f-6x9.fnt",
        bank = 0,
        align = 0,
        text = "",
        x = 160,
        y = 120,
        scaleX = 1.5,
        scaleY = 1.5,
        r = 255,
        g = 255,
        b = 255
    })

    -- Player action menu items
    live_lobby.gfx.actionItems = {}
    for i = 1, 3 do
        live_lobby.gfx.actionItems[i] = text:create({
            font = "font/jg.fnt",
            bank = 0,
            align = 0,
            text = "",
            x = 160,
            y = 130 + (i - 1) * 25,
            scaleX = 1.6,
            scaleY = 1.6,
            r = 255,
            g = 255,
            b = 255
        })
    end

    -- Overlays / Rectangles
    live_lobby.gfx.bgOverlay = rect:create({
        x1 = 0, y1 = 0, x2 = 320, y2 = 240,
        r = 0, g = 0, b = 30,
        src = 128, dst = 128
    })

    live_lobby.gfx.headerBar = rect:create({
        x1 = 0, y1 = 0, x2 = 320, y2 = 50,
        r = 20, g = 40, b = 80,
        src = 200, dst = 56
    })

    live_lobby.gfx.footerBar = rect:create({
        x1 = 0, y1 = 215, x2 = 320, y2 = 240,
        r = 20, g = 40, b = 80,
        src = 200, dst = 56
    })

    live_lobby.gfx.selectionBar = rect:create({
        x1 = 20, y1 = 70, x2 = 300, y2 = 90,
        r = 80, g = 120, b = 200,
        src = 180, dst = 76
    })

    live_lobby.gfx.challengeBox = rect:create({
        x1 = 30, y1 = 60, x2 = 290, y2 = 180,
        r = 120, g = 20, b = 20,
        src = 220, dst = 36
    })

    live_lobby.gfxInitialized = true
end

-- ============================================================================
-- DRAWING FUNCTIONS
-- ============================================================================

function live_lobby.drawBackground()
    live_lobby.gfx.bgOverlay:draw()
    live_lobby.gfx.headerBar:draw()
    live_lobby.gfx.footerBar:draw()
end

function live_lobby.drawTitle()
    local pulse = math.abs(math.sin(live_lobby.animTimer * 0.05))
    local r = 200 + math.floor(55 * pulse)
    local g = 150 + math.floor(50 * pulse)
    live_lobby.gfx.title.r = r
    live_lobby.gfx.title.g = g
    live_lobby.gfx.title:draw()
    live_lobby.gfx.subtitle:draw()
end

function live_lobby.drawStatusBar()
    local d = live_lobby.data
    if d then
        local statusText = string.format("EN LIGNE: %d | MATCHS: %d | FILE: %d",
            d.players_online or 0, d.active_matches or 0, (d.queue_ranked or 0) + (d.queue_casual or 0))
        live_lobby.gfx.statusBar.text = statusText
    else
        live_lobby.gfx.statusBar.text = "Connexion au serveur..."
    end
    live_lobby.gfx.statusBar:draw()
end

function live_lobby.drawMenu()
    local selY = 68 + (live_lobby.selectedOption - 1) * 22
    live_lobby.gfx.selectionBar.y1 = selY
    live_lobby.gfx.selectionBar.y2 = selY + 20
    live_lobby.gfx.selectionBar:draw()

    local cursorX = 25 + math.floor(math.sin(live_lobby.animTimer * 0.15) * 3)
    live_lobby.gfx.cursor.x = cursorX
    live_lobby.gfx.cursor.y = selY + 2
    live_lobby.gfx.cursor:draw()

    for i, opt in ipairs(live_lobby.menuOptions) do
        local item = live_lobby.gfx.menuItems[i]
        if item then
            item.text = opt.icon .. " " .. opt.name
            if i == live_lobby.selectedOption then
                item.r = 255
                item.g = 255
                item.b = 100
            else
                item.r = 200
                item.g = 200
                item.b = 200
            end
            item:draw()
        end
    end
end

function live_lobby.drawPlayerList()
    live_lobby.gfx.sectionTitle.text = "JOUEURS EN LIGNE"
    live_lobby.gfx.sectionTitle:draw()

    local players = live_lobby.filteredPlayers
    if #players == 0 then players = live_lobby.onlinePlayers end

    if #players == 0 then
        live_lobby.gfx.playerItems[1].text = "Aucun joueur en ligne"
        live_lobby.gfx.playerItems[1].r = 150
        live_lobby.gfx.playerItems[1].g = 150
        live_lobby.gfx.playerItems[1].b = 150
        live_lobby.gfx.playerItems[1]:draw()
        return
    end

    local startIdx = math.max(1, live_lobby.selectedPlayer - 4)
    local endIdx = math.min(#players, startIdx + 7)

    for i = startIdx, endIdx do
        local displayIdx = i - startIdx + 1
        local p = players[i]
        local item = live_lobby.gfx.playerItems[displayIdx]

        if item and p then
            local isReal = p.isReal
            if isReal == nil then
                local pid = p.player_id or p.playerId or ""
                if pid == "" then
                    isReal = false
                else
                    isReal = not (string.find(pid, "^bot_") or string.find(pid, "^sim_") or string.find(pid, "^ai_"))
                end
            end

            local status = p.status or "ready"
            local statusIcon = "*"
            if status == "fighting" or status == "in_match" then
                statusIcon = "!"
            elseif status == "away" or status == "afk" then
                statusIcon = "-"
            end

            local typeTag = isReal and "[REEL]" or "[BOT]"
            local prefix = i == live_lobby.selectedPlayer and "> " or "  "

            item.text = string.format("%s%s %s %-12s ELO:%d",
                prefix, statusIcon, typeTag, p.username or "???", p.mmr or p.elo or 1000)

            if i == live_lobby.selectedPlayer then
                item.r = 255
                item.g = 255
                item.b = 100
            elseif isReal then
                item.r = 100
                item.g = 255
                item.b = 100
            else
                item.r = 100
                item.g = 150
                item.b = 255
            end

            item:draw()
        end
    end

    local selY = 63 + (math.min(live_lobby.selectedPlayer - startIdx + 1, 8) - 1) * 18
    live_lobby.gfx.selectionBar.y1 = selY
    live_lobby.gfx.selectionBar.y2 = selY + 16
    live_lobby.gfx.selectionBar:draw()
end

function live_lobby.drawPlayerAction()
    if not live_lobby.selectedPlayerData then return end
    local p = live_lobby.selectedPlayerData

    live_lobby.gfx.challengeBox.r = 30
    live_lobby.gfx.challengeBox.g = 30
    live_lobby.gfx.challengeBox.b = 60
    live_lobby.gfx.challengeBox:draw()

    local isReal = p.isReal
    if isReal == nil then
        local pid = p.player_id or p.playerId or ""
        isReal = not (string.find(pid, "^bot_") or string.find(pid, "^sim_") or string.find(pid, "^ai_"))
    end

    local typeLabel = isReal and "JOUEUR REEL" or "BOT SIMULE"
    live_lobby.gfx.challengeTitle.text = p.username or "???"
    live_lobby.gfx.challengeTitle.r = isReal and 100 or 100
    live_lobby.gfx.challengeTitle.g = isReal and 255 or 150
    live_lobby.gfx.challengeTitle.b = isReal and 100 or 255
    live_lobby.gfx.challengeTitle:draw()

    live_lobby.gfx.challengeDetails.text = string.format("%s | ELO: %d | %s",
        typeLabel, p.mmr or p.elo or 1000, p.rank or "Bronze")
    live_lobby.gfx.challengeDetails:draw()

    local actions = {"DEFIER EN DUEL", "VOIR PROFIL", "ANNULER"}
    for i, action in ipairs(actions) do
        local item = live_lobby.gfx.actionItems[i]
        if item then
            item.text = (i == live_lobby.playerActionOption and ">> " or "   ") .. action
            if i == live_lobby.playerActionOption then
                item.r = 255
                item.g = 255
                item.b = 100
            else
                item.r = 180
                item.g = 180
                item.b = 180
            end
            item:draw()
        end
    end
end

function live_lobby.drawChallengePopup()
    if not live_lobby.pendingChallenge then return end
    local c = live_lobby.pendingChallenge
    local timeLeft = math.ceil(live_lobby.challengeTimer / 60)

    live_lobby.gfx.challengeBox.r = 120
    live_lobby.gfx.challengeBox.g = 20
    live_lobby.gfx.challengeBox.b = 20
    live_lobby.gfx.challengeBox:draw()

    local flash = math.floor(live_lobby.animTimer * 0.2) % 2
    live_lobby.gfx.challengeTitle.text = "!!! DEFI RECU !!!"
    live_lobby.gfx.challengeTitle.r = flash == 0 and 255 or 255
    live_lobby.gfx.challengeTitle.g = flash == 0 and 255 or 50
    live_lobby.gfx.challengeTitle.b = flash == 0 and 50 or 50
    live_lobby.gfx.challengeTitle:draw()

    live_lobby.gfx.challengeDetails.text = string.format("%s vous defie! ELO: %d | %d sec",
        c.from or "???", c.mmr or 1000, timeLeft)
    live_lobby.gfx.challengeDetails:draw()

    live_lobby.gfx.actionItems[1].text = "[Z] ACCEPTER"
    live_lobby.gfx.actionItems[1].r = 100
    live_lobby.gfx.actionItems[1].g = 255
    live_lobby.gfx.actionItems[1].b = 100
    live_lobby.gfx.actionItems[1]:draw()

    live_lobby.gfx.actionItems[2].text = "[X] REFUSER"
    live_lobby.gfx.actionItems[2].r = 255
    live_lobby.gfx.actionItems[2].g = 100
    live_lobby.gfx.actionItems[2].b = 100
    live_lobby.gfx.actionItems[2]:draw()
end

function live_lobby.drawMessage()
    if live_lobby.message ~= "" then
        live_lobby.gfx.message.text = ">>> " .. live_lobby.message .. " <<<"
        live_lobby.gfx.message:draw()
    end

    if live_lobby.inMatchmaking then
        local dots = string.rep(".", (math.floor(live_lobby.animTimer * 0.1) % 4))
        live_lobby.gfx.message.text = "RECHERCHE EN COURS" .. dots .. " (" .. live_lobby.matchmakingTimer .. "s)"
        live_lobby.gfx.message:draw()
    end
end

function live_lobby.drawFooter()
    if live_lobby.viewMode == "players" then
        live_lobby.gfx.footer.text = "[Z] Selectionner  [A] Rechercher  [X] Retour"
    elseif live_lobby.playerActionMode then
        live_lobby.gfx.footer.text = "[Z] Confirmer  [X] Annuler"
    elseif live_lobby.pendingChallenge then
        live_lobby.gfx.footer.text = "[Z] Accepter  [X] Refuser"
    else
        live_lobby.gfx.footer.text = "[HAUT/BAS] Naviguer  [Z] Confirmer  [ENTER/ECHAP] Retour"
    end
    live_lobby.gfx.footer:draw()
end

function live_lobby.draw()
    if not live_lobby.active then return end

    live_lobby.initGraphics()
    live_lobby.animTimer = live_lobby.animTimer + 1

    live_lobby.drawBackground()
    live_lobby.drawTitle()
    live_lobby.drawStatusBar()

    if live_lobby.pendingChallenge then
        live_lobby.drawChallengePopup()
    elseif live_lobby.playerActionMode then
        live_lobby.drawPlayerAction()
    elseif live_lobby.viewMode == "players" then
        live_lobby.drawPlayerList()
    else
        live_lobby.drawMenu()
    end

    live_lobby.drawMessage()
    live_lobby.drawFooter()
end

-- ============================================================================
-- DATA FUNCTIONS
-- ============================================================================

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
                if data.online_players then
                    live_lobby.onlinePlayers = data.online_players
                end
                return true
            end
        end
    end
    return false
end

function live_lobby.loadPlayers()
    local path = "save/online_players.json"
    local file = io.open(path, "r")
    if file then
        local content = file:read("*all")
        file:close()
        if content and content ~= "" then
            local success, data = pcall(json.decode, content)
            if success and data then
                live_lobby.onlinePlayers = data
                live_lobby.filterPlayers()
            end
        end
    end
end

function live_lobby.filterPlayers()
    if live_lobby.searchText == "" then
        live_lobby.filteredPlayers = live_lobby.onlinePlayers
    else
        live_lobby.filteredPlayers = {}
        local search = string.lower(live_lobby.searchText)
        for _, p in ipairs(live_lobby.onlinePlayers) do
            if string.find(string.lower(p.username or ""), search) then
                table.insert(live_lobby.filteredPlayers, p)
            end
        end
    end
end

function live_lobby.checkIncomingChallenge()
    local path = "save/incoming_challenge.json"
    local file = io.open(path, "r")
    if file then
        local content = file:read("*all")
        file:close()
        if content and content ~= "" then
            local success, data = pcall(json.decode, content)
            if success and data and data.from then
                live_lobby.pendingChallenge = data
                live_lobby.challengeTimer = 15 * 60
                os.remove(path)
            end
        end
    end
end

function live_lobby.sendChallenge(player)
    local request = {
        type = "send_challenge",
        from = "LocalPlayer",
        to = player.username,
        to_id = player.player_id,
        timestamp = os.date("%Y-%m-%d %H:%M:%S")
    }
    local file = io.open("save/challenge_request.json", "w")
    if file then
        file:write(json.encode(request))
        file:close()
    end
    live_lobby.challengeSent = true
    live_lobby.challengeTarget = player.username
    live_lobby.showMessage("Defi envoye a " .. player.username .. "!")
end

function live_lobby.acceptChallenge()
    if not live_lobby.pendingChallenge then return end
    local request = {
        type = "accept_challenge",
        challenge_id = live_lobby.pendingChallenge.challenge_id,
        from = live_lobby.pendingChallenge.from,
        timestamp = os.date("%Y-%m-%d %H:%M:%S")
    }
    local file = io.open("save/challenge_response.json", "w")
    if file then
        file:write(json.encode(request))
        file:close()
    end
    live_lobby.showMessage("DEFI ACCEPTE! Lancement du match...")
    live_lobby.pendingChallenge = nil
    live_lobby.challengeTimer = 0
    live_lobby.nextAction = "versus"
    live_lobby.close()
end

function live_lobby.declineChallenge()
    if not live_lobby.pendingChallenge then return end
    local request = {
        type = "decline_challenge",
        challenge_id = live_lobby.pendingChallenge.challenge_id,
        from = live_lobby.pendingChallenge.from,
        timestamp = os.date("%Y-%m-%d %H:%M:%S")
    }
    local file = io.open("save/challenge_response.json", "w")
    if file then
        file:write(json.encode(request))
        file:close()
    end
    live_lobby.showMessage("Defi refuse")
    live_lobby.pendingChallenge = nil
    live_lobby.challengeTimer = 0
end

function live_lobby.showMessage(msg)
    live_lobby.message = msg
    live_lobby.messageTimer = 90
end

-- ============================================================================
-- INPUT HANDLING
-- ============================================================================

function live_lobby.handleInput(cmd)
    if not live_lobby.active then return false end

    if live_lobby.messageTimer > 0 then
        live_lobby.messageTimer = live_lobby.messageTimer - 1
        if live_lobby.messageTimer <= 0 then live_lobby.message = "" end
    end

    if live_lobby.pendingChallenge then
        live_lobby.challengeTimer = live_lobby.challengeTimer - 1
        if live_lobby.challengeTimer <= 0 then
            live_lobby.showMessage("Defi expire!")
            live_lobby.pendingChallenge = nil
        end

        if commandGetState(cmd, "a") then
            live_lobby.acceptChallenge()
            return true
        end

        if commandGetState(cmd, "b") or commandGetState(cmd, "s") then
            live_lobby.declineChallenge()
            return true
        end
        return true
    end

    if live_lobby.inMatchmaking then
        live_lobby.matchmakingTimer = live_lobby.matchmakingTimer + 1
        if commandGetState(cmd, "s") then
            live_lobby.inMatchmaking = false
            live_lobby.showMessage("Matchmaking annule")
        end
        return true
    end

    if live_lobby.playerActionMode then
        if commandGetState(cmd, "$U") then
            if live_lobby.playerActionOption > 1 then
                live_lobby.playerActionOption = live_lobby.playerActionOption - 1
            end
            return true
        end

        if commandGetState(cmd, "$D") then
            if live_lobby.playerActionOption < 3 then
                live_lobby.playerActionOption = live_lobby.playerActionOption + 1
            end
            return true
        end

        if commandGetState(cmd, "a") then
            local p = live_lobby.selectedPlayerData
            if live_lobby.playerActionOption == 1 then
                local status = p.status or "ready"
                if status == "ready" or status == "online" or status == "in_lobby" then
                    live_lobby.sendChallenge(p)
                else
                    live_lobby.showMessage("Ce joueur n'est pas disponible!")
                end
            elseif live_lobby.playerActionOption == 2 then
                live_lobby.showMessage(string.format("%s - ELO:%d W:%d L:%d",
                    p.username or "?", p.mmr or 1000, p.wins or 0, p.losses or 0))
            end
            live_lobby.playerActionMode = false
            live_lobby.selectedPlayerData = nil
            return true
        end

        if commandGetState(cmd, "b") or commandGetState(cmd, "s") then
            live_lobby.playerActionMode = false
            live_lobby.selectedPlayerData = nil
            return true
        end

        return true
    end

    if live_lobby.searchMode then
        if commandGetState(cmd, "b") or commandGetState(cmd, "s") then
            live_lobby.searchMode = false
            live_lobby.filterPlayers()
            return true
        end

        if commandGetState(cmd, "a") then
            if #live_lobby.searchText > 0 then
                live_lobby.searchText = string.sub(live_lobby.searchText, 1, -2)
                live_lobby.filterPlayers()
            end
            return true
        end

        return true
    end

    if live_lobby.viewMode == "players" then
        local players = live_lobby.filteredPlayers
        if #players == 0 then players = live_lobby.onlinePlayers end

        if commandGetState(cmd, "$U") then
            if live_lobby.selectedPlayer > 1 then
                live_lobby.selectedPlayer = live_lobby.selectedPlayer - 1
            end
            return true
        end

        if commandGetState(cmd, "$D") then
            if live_lobby.selectedPlayer < #players then
                live_lobby.selectedPlayer = live_lobby.selectedPlayer + 1
            end
            return true
        end

        if commandGetState(cmd, "x") then
            live_lobby.searchMode = true
            live_lobby.showMessage("Mode recherche: tapez le nom")
            return true
        end

        if commandGetState(cmd, "a") then
            local player = players[live_lobby.selectedPlayer]
            if player then
                live_lobby.playerActionMode = true
                live_lobby.playerActionOption = 1
                live_lobby.selectedPlayerData = player
            end
            return true
        end

        if commandGetState(cmd, "b") or commandGetState(cmd, "s") then
            live_lobby.viewMode = "menu"
            live_lobby.searchText = ""
            live_lobby.filterPlayers()
            return true
        end

        return true
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
        if opt and opt.action ~= "back" then
            live_lobby.executeAction(opt.action)
            return true
        elseif opt and opt.action == "back" then
            live_lobby.close()
            return true
        end
    end

    if commandGetState(cmd, "s") then
        live_lobby.close()
        return true
    end

    return false
end

function live_lobby.executeAction(action)
    if action == "ranked" then
        live_lobby.inMatchmaking = true
        live_lobby.matchmakingTimer = 0
        local request = {type = "matchmaking", player = "LocalPlayer", mode = "ranked", timestamp = os.date("%Y-%m-%d %H:%M:%S")}
        local file = io.open("save/matchmaking_request.json", "w")
        if file then file:write(json.encode(request)); file:close() end
        live_lobby.showMessage("Recherche match CLASSE...")
    elseif action == "casual" then
        live_lobby.inMatchmaking = true
        live_lobby.matchmakingTimer = 0
        local request = {type = "matchmaking", player = "LocalPlayer", mode = "casual", timestamp = os.date("%Y-%m-%d %H:%M:%S")}
        local file = io.open("save/matchmaking_request.json", "w")
        if file then file:write(json.encode(request)); file:close() end
        live_lobby.showMessage("Recherche match CASUAL...")
    elseif action == "players" then
        live_lobby.viewMode = "players"
        live_lobby.selectedPlayer = 1
        live_lobby.loadPlayers()
        live_lobby.showMessage("Selectionnez un joueur")
    elseif action == "ai_training" then
        live_lobby.nextAction = "training"
        live_lobby.close()
        return
    elseif action == "create" then
        local request = {type = "create_lobby", player = "LocalPlayer", timestamp = os.date("%Y-%m-%d %H:%M:%S")}
        local file = io.open("save/lobby_request.json", "w")
        if file then file:write(json.encode(request)); file:close() end
        live_lobby.nextAction = "versus"
        live_lobby.showMessage("Creation du lobby...")
        live_lobby.close()
        return
    elseif action == "leaderboard" then
        live_lobby.nextAction = "leaderboard"
        live_lobby.close()
    elseif action == "back" then
        live_lobby.close()
    end
end

-- ============================================================================
-- LIFECYCLE
-- ============================================================================

function live_lobby.open()
    live_lobby.loadData()
    live_lobby.loadPlayers()
    live_lobby.active = true
    live_lobby.selectedOption = 1
    live_lobby.selectedPlayer = 1
    live_lobby.viewMode = "menu"
    live_lobby.message = ""
    live_lobby.inMatchmaking = false
    live_lobby.pendingChallenge = nil
    live_lobby.challengeSent = false
    live_lobby.animTimer = 0
end

function live_lobby.close()
    live_lobby.active = false
    live_lobby.inMatchmaking = false
    live_lobby.viewMode = "menu"
    live_lobby.pendingChallenge = nil
    live_lobby.challengeSent = false
    live_lobby.playerActionMode = false
    live_lobby.selectedPlayerData = nil
    live_lobby.searchMode = false
    live_lobby.searchText = ""
end

function live_lobby.isActive()
    return live_lobby.active
end

function live_lobby.checkMatchStart()
    local path = "save/match_start.json"
    local file = io.open(path, "r")
    if file then
        local content = file:read("*all")
        file:close()
        if content and content ~= "" then
            local success, data = pcall(json.decode, content)
            if success and data and data.match_id then
                os.remove(path)
                live_lobby.nextAction = "versus"
                live_lobby.showMessage("MATCH TROUVE! Lancement...")
                live_lobby.inMatchmaking = false
                live_lobby.close()
                return true
            end
        end
    end
    return false
end

function live_lobby.update()
    if not live_lobby.active then return end
    local now = os.time()
    if now - live_lobby.lastUpdate >= live_lobby.updateInterval then
        live_lobby.loadData()
        live_lobby.loadPlayers()
        live_lobby.checkIncomingChallenge()
        if live_lobby.inMatchmaking then
            live_lobby.checkMatchStart()
        end
        live_lobby.lastUpdate = now
    end
end

function live_lobby.init()
    live_lobby.loadData()
end

function live_lobby.getDisplayText()
    return "Use live_lobby.draw() for graphical UI"
end

live_lobby.init()
return live_lobby
