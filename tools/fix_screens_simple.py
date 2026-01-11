#!/usr/bin/env python3
"""Revert to simpler working version of online screens"""

main_lua_path = r"D:\KOF Ultimate Online\external\script\main.lua"

with open(main_lua_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the LEADERBOARD handler with simpler version
import re

# Simple working leaderboard
new_lb = '''--LEADERBOARD (KOF Ultimate Online)
main.t_itemname['rankings'] = function()
	if leaderboard_screen then
		leaderboard_screen.open()
		local txt = text:create({font = -1, bank = 0, align = -1, text = "", x = 50, y = 40, scaleX = 1, scaleY = 1, r = 255, g = 255, b = 255})
		local startTime = os.clock()
		while leaderboard_screen.isActive() do
			main.f_cmdInput()
			-- Skip first 0.2 seconds to avoid accidental close
			if os.clock() - startTime > 0.2 then
				for i = 1, #main.t_cmd do
					leaderboard_screen.handleInput(main.t_cmd[i])
				end
			end
			clearColor(20, 20, 50)
			local displayText = leaderboard_screen.getDisplayText()
			local lines = {}
			for line in displayText:gmatch("[^\\n]+") do
				table.insert(lines, line)
			end
			for i, line in ipairs(lines) do
				txt:update({text = line, y = 35 + (i-1) * 16})
				txt:draw()
			end
			refresh()
		end
	end
	return nil
end'''

new_pf = '''--MY PROFILE (KOF Ultimate Online)
main.t_itemname['profile'] = function()
	if profile_screen then
		profile_screen.open("LocalPlayer")
		local txt = text:create({font = -1, bank = 0, align = -1, text = "", x = 50, y = 40, scaleX = 1, scaleY = 1, r = 255, g = 255, b = 255})
		local startTime = os.clock()
		while profile_screen.isActive() do
			main.f_cmdInput()
			if os.clock() - startTime > 0.2 then
				for i = 1, #main.t_cmd do
					profile_screen.handleInput(main.t_cmd[i])
				end
			end
			clearColor(20, 20, 50)
			local displayText = profile_screen.getDisplayText()
			local lines = {}
			for line in displayText:gmatch("[^\\n]+") do
				table.insert(lines, line)
			end
			for i, line in ipairs(lines) do
				txt:update({text = line, y = 35 + (i-1) * 16})
				txt:draw()
			end
			refresh()
		end
	end
	return nil
end'''

new_lby = '''--LIVE LOBBY (KOF Ultimate Online)
main.t_itemname['lobby'] = function()
	if live_lobby then
		live_lobby.open()
		local txt = text:create({font = -1, bank = 0, align = -1, text = "", x = 50, y = 25, scaleX = 1, scaleY = 1, r = 255, g = 255, b = 255})
		local startTime = os.clock()
		while live_lobby.isActive() do
			main.f_cmdInput()
			live_lobby.update()
			if os.clock() - startTime > 0.2 then
				for i = 1, #main.t_cmd do
					live_lobby.handleInput(main.t_cmd[i])
				end
			end
			clearColor(20, 20, 50)
			local displayText = live_lobby.getDisplayText()
			local lines = {}
			for line in displayText:gmatch("[^\\n]+") do
				table.insert(lines, line)
			end
			for i, line in ipairs(lines) do
				txt:update({text = line, y = 22 + (i-1) * 15})
				txt:draw()
			end
			refresh()
		end
	end
	return nil
end'''

# Replace using regex to find the handlers
pattern_lb = r'--LEADERBOARD \(KOF Ultimate Online\)\nmain\.t_itemname\[\'rankings\'\] = function\(\).*?return nil\nend'
pattern_pf = r'--MY PROFILE \(KOF Ultimate Online\)\nmain\.t_itemname\[\'profile\'\] = function\(\).*?return nil\nend'
pattern_lby = r'--LIVE LOBBY \(KOF Ultimate Online\)\nmain\.t_itemname\[\'lobby\'\] = function\(\).*?return nil\nend'

content = re.sub(pattern_lb, new_lb, content, flags=re.DOTALL)
content = re.sub(pattern_pf, new_pf, content, flags=re.DOTALL)
content = re.sub(pattern_lby, new_lby, content, flags=re.DOTALL)

with open(main_lua_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed screens with simpler working version!")
print("- Using font = -1 (system font)")
print("- Added input delay to prevent accidental close")
print("- Dark blue background (20, 20, 50)")
