#!/usr/bin/env python3
"""Fix online screens to use proper background rendering"""

import os
import re

main_lua_path = r"D:\KOF Ultimate Online\external\script\main.lua"

# Read the file
with open(main_lua_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix LEADERBOARD screen
old_leaderboard = '''--LEADERBOARD (KOF Ultimate Online)
main.t_itemname['rankings'] = function()
	if leaderboard_screen then
		leaderboard_screen.open()
		-- Create text object for leaderboard display
		local txt = text:create({
			font = 3,
			bank = 0,
			align = -1,
			text = "",
			x = 50,
			y = 60,
			scaleX = 1,
			scaleY = 1,
			r = 255, g = 255, b = 255,
			window = {0, 0, 640, 480}
		})
		while leaderboard_screen.isActive() do
			main.f_cmdInput()
			for i = 1, #main.t_cmd do
				leaderboard_screen.handleInput(main.t_cmd[i])
			end
			clearColor(10, 10, 30)
			local displayText = leaderboard_screen.getDisplayText()
			local lines = {}
			for line in displayText:gmatch("[^\\n]+") do
				table.insert(lines, line)
			end
			for i, line in ipairs(lines) do
				txt:update({text = line, y = 50 + (i-1) * 20})
				txt:draw()
			end
			refresh()
		end
	else
		print("[KOF Online] Leaderboard screen not loaded")
	end
	return nil
end'''

new_leaderboard = '''--LEADERBOARD (KOF Ultimate Online)
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

# Fix PROFILE screen
old_profile = '''--MY PROFILE (KOF Ultimate Online)
main.t_itemname['profile'] = function()
	if profile_screen then
		profile_screen.open("LocalPlayer")
		local txt = text:create({
			font = 3,
			bank = 0,
			align = -1,
			text = "",
			x = 50,
			y = 60,
			scaleX = 1,
			scaleY = 1,
			r = 255, g = 255, b = 255,
			window = {0, 0, 640, 480}
		})
		while profile_screen.isActive() do
			main.f_cmdInput()
			for i = 1, #main.t_cmd do
				profile_screen.handleInput(main.t_cmd[i])
			end
			clearColor(10, 10, 30)
			local displayText = profile_screen.getDisplayText()
			local lines = {}
			for line in displayText:gmatch("[^\\n]+") do
				table.insert(lines, line)
			end
			for i, line in ipairs(lines) do
				txt:update({text = line, y = 40 + (i-1) * 20})
				txt:draw()
			end
			refresh()
		end
	else
		print("[KOF Online] Profile screen not loaded")
	end
	return nil
end'''

new_profile = '''--MY PROFILE (KOF Ultimate Online)
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

# Fix LOBBY screen
old_lobby = '''--LIVE LOBBY (KOF Ultimate Online)
main.t_itemname['lobby'] = function()
	if live_lobby then
		live_lobby.open()
		local txt = text:create({
			font = 3,
			bank = 0,
			align = -1,
			text = "",
			x = 50,
			y = 30,
			scaleX = 1,
			scaleY = 1,
			r = 255, g = 255, b = 255,
			window = {0, 0, 640, 480}
		})
		while live_lobby.isActive() do
			main.f_cmdInput()
			live_lobby.update()
			for i = 1, #main.t_cmd do
				live_lobby.handleInput(main.t_cmd[i])
			end
			clearColor(10, 10, 30)
			local displayText = live_lobby.getDisplayText()
			local lines = {}
			for line in displayText:gmatch("[^\\n]+") do
				table.insert(lines, line)
			end
			for i, line in ipairs(lines) do
				txt:update({text = line, y = 25 + (i-1) * 18})
				txt:draw()
			end
			refresh()
		end
	else
		print("[KOF Online] Live lobby screen not loaded")
	end
	return nil
end'''

new_lobby = '''--LIVE LOBBY (KOF Ultimate Online)
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

# Apply replacements
content = content.replace(old_leaderboard, new_leaderboard)
content = content.replace(old_profile, new_profile)
content = content.replace(old_lobby, new_lobby)

# Write the file
with open(main_lua_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed online screens with proper background rendering!")
print("- Leaderboard: uses motif background")
print("- Profile: uses motif background")
print("- Lobby: uses motif background")
