#!/usr/bin/env python3
"""Fix the crash in online screens by using safe defaults"""

main_lua_path = r"D:\KOF Ultimate Online\external\script\main.lua"

with open(main_lua_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix leaderboard crash - use safe font defaults
old_lb = '''--LEADERBOARD (KOF Ultimate Online)
main.t_itemname['rankings'] = function()
	if leaderboard_screen then
		leaderboard_screen.open()
		main.f_bgReset(motif[main.background].bg)
		local txt = text:create({
			font = motif.title_info.menu_item_font[1],
			bank = motif.title_info.menu_item_font[2],
			align = -1,
			text = "",
			x = 60,
			y = 50,
			scaleX = motif.title_info.menu_item_font_scale[1],
			scaleY = motif.title_info.menu_item_font_scale[2],
			r = 255, g = 255, b = 255,
			window = {0, 0, motif.info.localcoord[1], motif.info.localcoord[2]}
		})
		while leaderboard_screen.isActive() do
			main.f_cmdInput()
			for i = 1, #main.t_cmd do
				leaderboard_screen.handleInput(main.t_cmd[i])
			end
			clearColor(motif[main.background].bgclearcolor[1], motif[main.background].bgclearcolor[2], motif[main.background].bgclearcolor[3])
			bgDraw(motif[main.background].bg, false)
			local displayText = leaderboard_screen.getDisplayText()
			local lines = {}
			for line in displayText:gmatch("[^\\n]+") do
				table.insert(lines, line)
			end
			for i, line in ipairs(lines) do
				txt:update({text = line, y = 40 + (i-1) * 18})
				txt:draw()
			end
			bgDraw(motif[main.background].bg, true)
			refresh()
		end
	else
		print("[KOF Online] Leaderboard screen not loaded")
	end
	return nil
end'''

new_lb = '''--LEADERBOARD (KOF Ultimate Online)
main.t_itemname['rankings'] = function()
	if leaderboard_screen then
		leaderboard_screen.open()
		main.f_bgReset(motif[main.background].bg)
		local txt = text:create({font = 2, bank = 0, align = -1, text = "", x = 60, y = 50, scaleX = 1, scaleY = 1, r = 255, g = 255, b = 255})
		while leaderboard_screen.isActive() do
			main.f_cmdInput()
			for i = 1, #main.t_cmd do
				leaderboard_screen.handleInput(main.t_cmd[i])
			end
			clearColor(motif[main.background].bgclearcolor[1], motif[main.background].bgclearcolor[2], motif[main.background].bgclearcolor[3])
			bgDraw(motif[main.background].bg, false)
			local displayText = leaderboard_screen.getDisplayText()
			local lines = {}
			for line in displayText:gmatch("[^\\n]+") do
				table.insert(lines, line)
			end
			for i, line in ipairs(lines) do
				txt:update({text = line, y = 40 + (i-1) * 18})
				txt:draw()
			end
			bgDraw(motif[main.background].bg, true)
			refresh()
		end
	end
	return nil
end'''

old_pf = '''--MY PROFILE (KOF Ultimate Online)
main.t_itemname['profile'] = function()
	if profile_screen then
		profile_screen.open("LocalPlayer")
		main.f_bgReset(motif[main.background].bg)
		local txt = text:create({
			font = motif.title_info.menu_item_font[1],
			bank = motif.title_info.menu_item_font[2],
			align = -1,
			text = "",
			x = 60,
			y = 40,
			scaleX = motif.title_info.menu_item_font_scale[1],
			scaleY = motif.title_info.menu_item_font_scale[2],
			r = 255, g = 255, b = 255,
			window = {0, 0, motif.info.localcoord[1], motif.info.localcoord[2]}
		})
		while profile_screen.isActive() do
			main.f_cmdInput()
			for i = 1, #main.t_cmd do
				profile_screen.handleInput(main.t_cmd[i])
			end
			clearColor(motif[main.background].bgclearcolor[1], motif[main.background].bgclearcolor[2], motif[main.background].bgclearcolor[3])
			bgDraw(motif[main.background].bg, false)
			local displayText = profile_screen.getDisplayText()
			local lines = {}
			for line in displayText:gmatch("[^\\n]+") do
				table.insert(lines, line)
			end
			for i, line in ipairs(lines) do
				txt:update({text = line, y = 35 + (i-1) * 18})
				txt:draw()
			end
			bgDraw(motif[main.background].bg, true)
			refresh()
		end
	else
		print("[KOF Online] Profile screen not loaded")
	end
	return nil
end'''

new_pf = '''--MY PROFILE (KOF Ultimate Online)
main.t_itemname['profile'] = function()
	if profile_screen then
		profile_screen.open("LocalPlayer")
		main.f_bgReset(motif[main.background].bg)
		local txt = text:create({font = 2, bank = 0, align = -1, text = "", x = 60, y = 40, scaleX = 1, scaleY = 1, r = 255, g = 255, b = 255})
		while profile_screen.isActive() do
			main.f_cmdInput()
			for i = 1, #main.t_cmd do
				profile_screen.handleInput(main.t_cmd[i])
			end
			clearColor(motif[main.background].bgclearcolor[1], motif[main.background].bgclearcolor[2], motif[main.background].bgclearcolor[3])
			bgDraw(motif[main.background].bg, false)
			local displayText = profile_screen.getDisplayText()
			local lines = {}
			for line in displayText:gmatch("[^\\n]+") do
				table.insert(lines, line)
			end
			for i, line in ipairs(lines) do
				txt:update({text = line, y = 35 + (i-1) * 18})
				txt:draw()
			end
			bgDraw(motif[main.background].bg, true)
			refresh()
		end
	end
	return nil
end'''

old_lby = '''--LIVE LOBBY (KOF Ultimate Online)
main.t_itemname['lobby'] = function()
	if live_lobby then
		live_lobby.open()
		main.f_bgReset(motif[main.background].bg)
		local txt = text:create({
			font = motif.title_info.menu_item_font[1],
			bank = motif.title_info.menu_item_font[2],
			align = -1,
			text = "",
			x = 60,
			y = 30,
			scaleX = motif.title_info.menu_item_font_scale[1],
			scaleY = motif.title_info.menu_item_font_scale[2],
			r = 255, g = 255, b = 255,
			window = {0, 0, motif.info.localcoord[1], motif.info.localcoord[2]}
		})
		while live_lobby.isActive() do
			main.f_cmdInput()
			live_lobby.update()
			for i = 1, #main.t_cmd do
				live_lobby.handleInput(main.t_cmd[i])
			end
			clearColor(motif[main.background].bgclearcolor[1], motif[main.background].bgclearcolor[2], motif[main.background].bgclearcolor[3])
			bgDraw(motif[main.background].bg, false)
			local displayText = live_lobby.getDisplayText()
			local lines = {}
			for line in displayText:gmatch("[^\\n]+") do
				table.insert(lines, line)
			end
			for i, line in ipairs(lines) do
				txt:update({text = line, y = 25 + (i-1) * 16})
				txt:draw()
			end
			bgDraw(motif[main.background].bg, true)
			refresh()
		end
	else
		print("[KOF Online] Live lobby screen not loaded")
	end
	return nil
end'''

new_lby = '''--LIVE LOBBY (KOF Ultimate Online)
main.t_itemname['lobby'] = function()
	if live_lobby then
		live_lobby.open()
		main.f_bgReset(motif[main.background].bg)
		local txt = text:create({font = 2, bank = 0, align = -1, text = "", x = 60, y = 30, scaleX = 1, scaleY = 1, r = 255, g = 255, b = 255})
		while live_lobby.isActive() do
			main.f_cmdInput()
			live_lobby.update()
			for i = 1, #main.t_cmd do
				live_lobby.handleInput(main.t_cmd[i])
			end
			clearColor(motif[main.background].bgclearcolor[1], motif[main.background].bgclearcolor[2], motif[main.background].bgclearcolor[3])
			bgDraw(motif[main.background].bg, false)
			local displayText = live_lobby.getDisplayText()
			local lines = {}
			for line in displayText:gmatch("[^\\n]+") do
				table.insert(lines, line)
			end
			for i, line in ipairs(lines) do
				txt:update({text = line, y = 25 + (i-1) * 16})
				txt:draw()
			end
			bgDraw(motif[main.background].bg, true)
			refresh()
		end
	end
	return nil
end'''

content = content.replace(old_lb, new_lb)
content = content.replace(old_pf, new_pf)
content = content.replace(old_lby, new_lby)

with open(main_lua_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed crashes with safe font defaults!")
