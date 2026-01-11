-- ============================================================================
-- KOF ULTIMATE ONLINE - AI TRAINING (GRAPHICAL UI)
-- ============================================================================

ai_training = ai_training or {}

ai_training.active = false
ai_training.playerELO = 1200
ai_training.botELO = 1200
ai_training.botName = "AI_Sparring_Partner"
ai_training.difficulty = 4
ai_training.message = ""
ai_training.messageTimer = 0
ai_training.selectedOption = 1
ai_training.animTimer = 0

ai_training.difficultyLevels = {
    {elo_range = {0, 1100}, difficulty = 2, name = "Beginner Bot"},
    {elo_range = {1100, 1200}, difficulty = 3, name = "Rookie Bot"},
    {elo_range = {1200, 1300}, difficulty = 4, name = "Bronze Bot"},
    {elo_range = {1300, 1400}, difficulty = 5, name = "Silver Bot"},
    {elo_range = {1400, 1500}, difficulty = 6, name = "Gold Bot"},
    {elo_range = {1500, 1600}, difficulty = 7, name = "Platinum Bot"},
    {elo_range = {1600, 9999}, difficulty = 8, name = "Master Bot"}
}

ai_training.menuOptions = {
    {name = "FACILE", mode = "easy", desc = "ELO -200", color = {100, 255, 100}},
    {name = "NORMAL", mode = "same_elo", desc = "Votre niveau", color = {255, 255, 100}},
    {name = "DIFFICILE", mode = "hard", desc = "ELO +200", color = {255, 150, 100}},
    {name = "DEFI", mode = "challenge", desc = "ELO +400", color = {255, 100, 100}},
    {name = "RETOUR", mode = "back", desc = "", color = {150, 150, 150}}
}

-- ============================================================================
-- GRAPHICS INITIALIZATION
-- ============================================================================

ai_training.gfx = {}
ai_training.gfxInitialized = false

function ai_training.initGraphics()
    if ai_training.gfxInitialized then return end

    -- Background
    ai_training.gfx.bgOverlay = rect:create({
        x1 = 0, y1 = 0, x2 = 320, y2 = 240,
        r = 10, g = 20, b = 40, src = 200, dst = 56
    })

    -- Header
    ai_training.gfx.headerBar = rect:create({
        x1 = 0, y1 = 0, x2 = 320, y2 = 55,
        r = 50, g = 30, b = 80, src = 220, dst = 36
    })

    -- Menu box
    ai_training.gfx.menuBox = rect:create({
        x1 = 40, y1 = 70, x2 = 280, y2 = 195,
        r = 30, g = 20, b = 60, src = 200, dst = 56
    })

    -- Selection bar
    ai_training.gfx.selectionBar = rect:create({
        x1 = 45, y1 = 80, x2 = 275, y2 = 100,
        r = 100, g = 80, b = 180, src = 180, dst = 76
    })

    -- Footer
    ai_training.gfx.footerBar = rect:create({
        x1 = 0, y1 = 210, x2 = 320, y2 = 240,
        r = 50, g = 30, b = 80, src = 220, dst = 36
    })

    -- Title
    ai_training.gfx.title = text:create({
        font = "font/jg.fnt", bank = 0, align = 0,
        text = "AI TRAINING", x = 160, y = 8,
        scaleX = 2.5, scaleY = 2.5, r = 200, g = 150, b = 255
    })

    -- Subtitle
    ai_training.gfx.subtitle = text:create({
        font = "font/f-6x9.fnt", bank = 0, align = 0,
        text = "", x = 160, y = 38,
        scaleX = 1.3, scaleY = 1.3, r = 255, g = 255, b = 200
    })

    -- Menu items
    ai_training.gfx.menuItems = {}
    for i = 1, 5 do
        ai_training.gfx.menuItems[i] = {
            name = text:create({
                font = "font/jg.fnt", bank = 0, align = -1,
                text = "", x = 55, y = 75 + (i - 1) * 23,
                scaleX = 1.6, scaleY = 1.6, r = 255, g = 255, b = 255
            }),
            desc = text:create({
                font = "font/f-6x9.fnt", bank = 0, align = 1,
                text = "", x = 265, y = 78 + (i - 1) * 23,
                scaleX = 1.1, scaleY = 1.1, r = 180, g = 180, b = 180
            })
        }
    end

    -- Cursor
    ai_training.gfx.cursor = text:create({
        font = "font/jg.fnt", bank = 0, align = -1,
        text = ">>", x = 42, y = 75,
        scaleX = 1.4, scaleY = 1.4, r = 255, g = 255, b = 0
    })

    -- Message
    ai_training.gfx.message = text:create({
        font = "font/jg.fnt", bank = 0, align = 0,
        text = "", x = 160, y = 198,
        scaleX = 1.2, scaleY = 1.2, r = 255, g = 255, b = 100
    })

    -- Footer
    ai_training.gfx.footer = text:create({
        font = "font/f-6x9.fnt", bank = 0, align = 0,
        text = "[Z] Selectionner  [ENTER/ESC] Retour", x = 160, y = 222,
        scaleX = 1.1, scaleY = 1.1, r = 200, g = 200, b = 200
    })

    ai_training.gfxInitialized = true
end

-- ============================================================================
-- DATA FUNCTIONS
-- ============================================================================

function ai_training.loadPlayerELO()
    local path = "save/player_profile.json"
    local file = io.open(path, "r")
    if file then
        local content = file:read("*all")
        file:close()
        if content and content ~= "" then
            local success, data = pcall(json.decode, content)
            if success and data and data.elo then
                ai_training.playerELO = data.elo
                return true
            end
        end
    end
    ai_training.playerELO = 1200
    return false
end

function ai_training.calculateBotDifficulty(targetELO)
    for _, level in ipairs(ai_training.difficultyLevels) do
        if targetELO >= level.elo_range[1] and targetELO <= level.elo_range[2] then
            ai_training.difficulty = level.difficulty
            ai_training.botName = level.name
            ai_training.botELO = targetELO
            return level.difficulty
        end
    end
    return 4
end

function ai_training.showMessage(msg)
    ai_training.message = msg
    ai_training.messageTimer = 90
end

-- ============================================================================
-- DRAWING
-- ============================================================================

function ai_training.draw()
    if not ai_training.active then return end

    ai_training.initGraphics()
    ai_training.animTimer = ai_training.animTimer + 1

    -- Background
    ai_training.gfx.bgOverlay:draw()
    ai_training.gfx.headerBar:draw()
    ai_training.gfx.menuBox:draw()
    ai_training.gfx.footerBar:draw()

    -- Title with pulse
    local pulse = math.abs(math.sin(ai_training.animTimer * 0.05))
    ai_training.gfx.title.r = 180 + math.floor(75 * pulse)
    ai_training.gfx.title.g = 130 + math.floor(50 * pulse)
    ai_training.gfx.title:draw()

    -- Subtitle with ELO
    ai_training.gfx.subtitle.text = string.format("Votre ELO: %d", ai_training.playerELO)
    ai_training.gfx.subtitle:draw()

    -- Selection bar
    local selY = 73 + (ai_training.selectedOption - 1) * 23
    ai_training.gfx.selectionBar.y1 = selY
    ai_training.gfx.selectionBar.y2 = selY + 20
    ai_training.gfx.selectionBar:draw()

    -- Cursor with animation
    local cursorX = 42 + math.floor(math.sin(ai_training.animTimer * 0.15) * 3)
    ai_training.gfx.cursor.x = cursorX
    ai_training.gfx.cursor.y = selY + 2
    ai_training.gfx.cursor:draw()

    -- Menu items
    for i, opt in ipairs(ai_training.menuOptions) do
        local item = ai_training.gfx.menuItems[i]
        if item then
            item.name.text = opt.name
            item.desc.text = opt.desc

            if i == ai_training.selectedOption then
                item.name.r, item.name.g, item.name.b = 255, 255, 100
            else
                item.name.r, item.name.g, item.name.b = opt.color[1], opt.color[2], opt.color[3]
            end

            item.name:draw()
            if opt.desc ~= "" then item.desc:draw() end
        end
    end

    -- Message
    if ai_training.message ~= "" then
        local flash = math.floor(ai_training.animTimer * 0.2) % 2
        ai_training.gfx.message.text = ai_training.message
        ai_training.gfx.message.g = flash == 0 and 255 or 200
        ai_training.gfx.message:draw()
    end

    -- Footer
    ai_training.gfx.footer:draw()
end

function ai_training.getDisplayText()
    return "Use ai_training.draw() for graphical UI"
end

-- ============================================================================
-- ACTIONS
-- ============================================================================

function ai_training.startTraining(mode)
    ai_training.loadPlayerELO()

    local targetELO = ai_training.playerELO
    if mode == "easy" then
        targetELO = ai_training.playerELO - 200
    elseif mode == "hard" then
        targetELO = ai_training.playerELO + 200
    elseif mode == "challenge" then
        targetELO = ai_training.playerELO + 400
    end

    ai_training.calculateBotDifficulty(targetELO)

    local config = {
        type = "ai_training",
        player_elo = ai_training.playerELO,
        bot_elo = ai_training.botELO,
        bot_name = ai_training.botName,
        ai_level = ai_training.difficulty,
        mode = mode,
        timestamp = os.date("%Y-%m-%d %H:%M:%S")
    }

    local file = io.open("save/ai_training_config.json", "w")
    if file then file:write(json.encode(config)); file:close() end

    ai_training.showMessage(string.format("vs %s (AI Lv.%d)", ai_training.botName, ai_training.difficulty))
    return true
end

-- ============================================================================
-- INPUT HANDLING
-- ============================================================================

function ai_training.handleInput(cmd)
    if not ai_training.active then return false end

    if ai_training.messageTimer > 0 then
        ai_training.messageTimer = ai_training.messageTimer - 1
        if ai_training.messageTimer <= 0 then ai_training.message = "" end
    end

    if commandGetState(cmd, "$U") then
        if ai_training.selectedOption > 1 then
            ai_training.selectedOption = ai_training.selectedOption - 1
        end
        return true
    end

    if commandGetState(cmd, "$D") then
        if ai_training.selectedOption < #ai_training.menuOptions then
            ai_training.selectedOption = ai_training.selectedOption + 1
        end
        return true
    end

    if commandGetState(cmd, "a") then
        local opt = ai_training.menuOptions[ai_training.selectedOption]
        if opt then
            if opt.mode == "back" then
                ai_training.close()
            else
                ai_training.startTraining(opt.mode)
            end
        end
        return true
    end

    if commandGetState(cmd, "s") or esc() then
        ai_training.close()
        return true
    end

    return false
end

-- ============================================================================
-- LIFECYCLE
-- ============================================================================

function ai_training.open()
    ai_training.loadPlayerELO()
    ai_training.active = true
    ai_training.selectedOption = 1
    ai_training.message = ""
    ai_training.animTimer = 0
end

function ai_training.close()
    ai_training.active = false
end

function ai_training.isActive()
    return ai_training.active
end

function ai_training.init()
    ai_training.loadPlayerELO()
end

ai_training.init()
return ai_training
