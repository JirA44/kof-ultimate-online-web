--[[
KOF ULTIMATE ONLINE - Silent Auto Test Mode
Lance des tests automatiques sans interaction clavier
Ecrit les resultats dans save/auto_test_results.json
]]--

local auto_test = {}

-- Configuration
auto_test.enabled = true
auto_test.max_matches = 5
auto_test.match_timeout = 3600  -- 60 secondes max par match (en frames)
auto_test.results_file = "save/auto_test_results.json"
auto_test.log_file = "save/auto_test_log.txt"

-- State
auto_test.initialized = false
auto_test.running = false
auto_test.matches_played = 0
auto_test.current_match_frames = 0
auto_test.test_start_time = nil
auto_test.results = {
    menus_tested = {},
    matches = {},
    errors = {},
    warnings = {}
}

-- Logging
local function log(msg)
    local timestamp = os.date("%Y-%m-%d %H:%M:%S")
    local line = string.format("[%s] %s\n", timestamp, msg)

    local file = io.open(auto_test.log_file, "a")
    if file then
        file:write(line)
        file:close()
    end
end

local function save_results()
    local file = io.open(auto_test.results_file, "w")
    if file then
        file:write(json.encode(auto_test.results))
        file:close()
    end
end

-- Test: Verify menu handlers exist
local function test_menu_handlers()
    log("Testing menu handlers...")

    local handlers_to_test = {
        "arcade", "versus", "teamarcade", "teamversus", "survival",
        "survivalcoop", "training", "trials", "options", "rankings",
        "profile", "lobby", "firebase", "battlenet", "demo", "randomtest"
    }

    local results = {}
    for _, handler_name in ipairs(handlers_to_test) do
        local exists = main.t_itemname[handler_name] ~= nil
        local is_function = type(main.t_itemname[handler_name]) == "function"

        results[handler_name] = {
            exists = exists,
            is_function = is_function,
            status = (exists and is_function) and "OK" or "MISSING"
        }

        if not exists or not is_function then
            table.insert(auto_test.results.errors, {
                type = "missing_handler",
                handler = handler_name,
                message = "Handler " .. handler_name .. " is missing or not a function"
            })
        end
    end

    auto_test.results.menus_tested = results
    log("Menu handlers test complete: " .. #handlers_to_test .. " tested")
    return results
end

-- Test: Verify required modules loaded
local function test_modules()
    log("Testing modules...")

    local modules_to_test = {
        {name = "leaderboard_screen", required = {"open", "close", "isActive", "handleInput"}},
        {name = "profile_screen", required = {"open", "close", "isActive", "handleInput"}},
        {name = "live_lobby", required = {"open", "close", "isActive", "handleInput", "loadLeaderboard"}},
        {name = "online_system", required = {}}
    }

    local results = {}
    for _, mod in ipairs(modules_to_test) do
        local module = _G[mod.name]
        local exists = module ~= nil
        local functions_ok = true
        local missing_funcs = {}

        if exists and mod.required then
            for _, func_name in ipairs(mod.required) do
                if type(module[func_name]) ~= "function" then
                    functions_ok = false
                    table.insert(missing_funcs, func_name)
                end
            end
        end

        results[mod.name] = {
            exists = exists,
            functions_ok = functions_ok,
            missing_functions = missing_funcs,
            status = (exists and functions_ok) and "OK" or "ERROR"
        }

        if not exists then
            table.insert(auto_test.results.warnings, {
                type = "missing_module",
                module = mod.name,
                message = "Module " .. mod.name .. " is not loaded"
            })
        elseif not functions_ok then
            table.insert(auto_test.results.errors, {
                type = "missing_functions",
                module = mod.name,
                functions = missing_funcs,
                message = "Module " .. mod.name .. " is missing functions: " .. table.concat(missing_funcs, ", ")
            })
        end
    end

    auto_test.results.modules_tested = results
    log("Modules test complete")
    return results
end

-- Test: Verify data files
local function test_data_files()
    log("Testing data files...")

    local files_to_test = {
        "save/leaderboard.json",
        "save/online_players.json",
        "save/match_history.json",
        "save/config.json",
        "save/stats.json"
    }

    local results = {}
    for _, filepath in ipairs(files_to_test) do
        local file = io.open(filepath, "r")
        local exists = file ~= nil
        local valid_json = false
        local content_size = 0

        if file then
            local content = file:read("*all")
            file:close()
            content_size = #content

            if content and content ~= "" then
                local success, _ = pcall(json.decode, content)
                valid_json = success
            end
        end

        results[filepath] = {
            exists = exists,
            valid_json = valid_json,
            size = content_size,
            status = (exists and valid_json) and "OK" or (exists and "INVALID_JSON" or "MISSING")
        }
    end

    auto_test.results.data_files_tested = results
    log("Data files test complete")
    return results
end

-- Test: Character loading
local function test_characters()
    log("Testing character loading...")

    local char_count = 0
    local errors = {}

    if main.t_randomChars then
        char_count = #main.t_randomChars
    end

    auto_test.results.characters = {
        count = char_count,
        status = char_count > 0 and "OK" or "NO_CHARACTERS"
    }

    if char_count == 0 then
        table.insert(auto_test.results.errors, {
            type = "no_characters",
            message = "No characters loaded in main.t_randomChars"
        })
    end

    log("Characters test complete: " .. char_count .. " characters loaded")
    return auto_test.results.characters
end

-- Test: Stage loading
local function test_stages()
    log("Testing stage loading...")

    local stage_count = 0

    if main.t_selStages then
        stage_count = #main.t_selStages
    end

    auto_test.results.stages = {
        count = stage_count,
        status = stage_count > 0 and "OK" or "NO_STAGES"
    }

    log("Stages test complete: " .. stage_count .. " stages loaded")
    return auto_test.results.stages
end

-- Generate final report
local function generate_report()
    log("Generating final report...")

    auto_test.results.summary = {
        test_date = os.date("%Y-%m-%d %H:%M:%S"),
        total_errors = #auto_test.results.errors,
        total_warnings = #auto_test.results.warnings,
        matches_played = auto_test.matches_played,
        status = #auto_test.results.errors == 0 and "PASS" or "FAIL"
    }

    save_results()

    -- Create readable report
    local report_path = "menu_test_reports/AUTO_TEST_REPORT.md"
    local report = io.open(report_path, "w")
    if report then
        report:write("# KOF Ultimate Online - Auto Test Report\n\n")
        report:write("**Date**: " .. os.date("%Y-%m-%d %H:%M:%S") .. "\n")
        report:write("**Status**: " .. auto_test.results.summary.status .. "\n\n")

        report:write("## Summary\n\n")
        report:write("| Metric | Value |\n")
        report:write("|--------|-------|\n")
        report:write("| Errors | " .. auto_test.results.summary.total_errors .. " |\n")
        report:write("| Warnings | " .. auto_test.results.summary.total_warnings .. " |\n")
        report:write("| Characters | " .. (auto_test.results.characters and auto_test.results.characters.count or "N/A") .. " |\n")
        report:write("| Stages | " .. (auto_test.results.stages and auto_test.results.stages.count or "N/A") .. " |\n\n")

        report:write("## Menu Handlers\n\n")
        report:write("| Handler | Status |\n")
        report:write("|---------|--------|\n")
        if auto_test.results.menus_tested then
            for name, data in pairs(auto_test.results.menus_tested) do
                report:write("| " .. name .. " | " .. data.status .. " |\n")
            end
        end

        report:write("\n## Modules\n\n")
        report:write("| Module | Status |\n")
        report:write("|--------|--------|\n")
        if auto_test.results.modules_tested then
            for name, data in pairs(auto_test.results.modules_tested) do
                report:write("| " .. name .. " | " .. data.status .. " |\n")
            end
        end

        report:write("\n## Data Files\n\n")
        report:write("| File | Status | Size |\n")
        report:write("|------|--------|------|\n")
        if auto_test.results.data_files_tested then
            for name, data in pairs(auto_test.results.data_files_tested) do
                report:write("| " .. name .. " | " .. data.status .. " | " .. data.size .. " |\n")
            end
        end

        if #auto_test.results.errors > 0 then
            report:write("\n## Errors\n\n")
            for _, err in ipairs(auto_test.results.errors) do
                report:write("- **" .. err.type .. "**: " .. err.message .. "\n")
            end
        end

        if #auto_test.results.warnings > 0 then
            report:write("\n## Warnings\n\n")
            for _, warn in ipairs(auto_test.results.warnings) do
                report:write("- **" .. warn.type .. "**: " .. warn.message .. "\n")
            end
        end

        report:write("\n---\n*Test executed silently without keyboard interaction*\n")
        report:close()
    end

    log("Report generated: " .. report_path)
end

-- Run all tests
local function run_tests()
    if auto_test.running then return end
    auto_test.running = true

    log("=== AUTO TEST STARTED ===")
    auto_test.test_start_time = os.time()

    -- Run tests
    test_menu_handlers()
    test_modules()
    test_data_files()
    test_characters()
    test_stages()

    -- Generate report
    generate_report()

    log("=== AUTO TEST COMPLETED ===")
    log("Errors: " .. #auto_test.results.errors .. ", Warnings: " .. #auto_test.results.warnings)

    auto_test.running = false
end

-- Hook into game loop
hook.add("loop", "silent_auto_test", function()
    if not auto_test.initialized and main and main.t_itemname then
        auto_test.initialized = true

        -- Clear old log
        local file = io.open(auto_test.log_file, "w")
        if file then file:close() end

        -- Run tests after a short delay (let game fully initialize)
        log("Silent Auto Test module initialized")

        -- Schedule test run
        local delay_frames = 120  -- 2 seconds at 60fps
        local frame_count = 0

        hook.add("loop", "auto_test_delayed_start", function()
            frame_count = frame_count + 1
            if frame_count >= delay_frames and not auto_test.running then
                hook.stop("loop", "auto_test_delayed_start")
                run_tests()
            end
        end)
    end
end)

log("Silent Auto Test module loaded")

return auto_test
