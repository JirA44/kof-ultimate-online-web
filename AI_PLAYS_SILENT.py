#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IA JOUE EN SILENCE
L'IA joue sans afficher les touches, screenshots seulement
"""

import pyautogui
import time
import random
from pathlib import Path
from datetime import datetime
import subprocess
import sys

# Rediriger stdout vers null pour silence total
class SilentOutput:
    def write(self, text):
        pass
    def flush(self):
        pass

class SilentAIPlayer:
    def __init__(self, game_dir):
        self.game_dir = Path(game_dir)
        self.game_exe = self.game_dir / "KOF_Ultimate_Online.exe"
        self.screenshots_dir = self.game_dir / "live_gameplay"
        self.screenshots_dir.mkdir(exist_ok=True)
        pyautogui.FAILSAFE = False

    def take_screenshot(self, name=""):
        """Prend un screenshot silencieusement"""
        timestamp = datetime.now().strftime("%H%M%S")
        filename = f"{timestamp}_{name}.png" if name else f"{timestamp}.png"
        filepath = self.screenshots_dir / filename
        screenshot = pyautogui.screenshot()
        screenshot.save(filepath)
        return filepath

    def press_key(self, key, duration=0.1):
        pyautogui.press(key)
        time.sleep(duration)

    def hold_key(self, key, duration=0.3):
        pyautogui.keyDown(key)
        time.sleep(duration)
        pyautogui.keyUp(key)

    def start_game(self):
        subprocess.Popen([str(self.game_exe)],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL)
        time.sleep(8)
        self.take_screenshot("game_start")

    def navigate_to_vs(self):
        time.sleep(2)
        self.press_key('return', 1)
        time.sleep(1)
        self.press_key('return', 1)
        self.take_screenshot("mode_selected")
        time.sleep(1)

    def select_random_character(self):
        moves = random.randint(3, 8)
        for i in range(moves):
            direction = random.choice(['up', 'down', 'left', 'right'])
            self.press_key(direction, 0.2)
            time.sleep(0.1)
        self.press_key('a', 0.5)
        time.sleep(1)

    def perform_random_action(self):
        action = random.choice([
            'attack_light', 'attack_medium', 'attack_heavy',
            'move_forward', 'move_backward', 'jump', 'crouch',
            'special_move', 'block', 'dash_forward', 'dash_backward'
        ])

        if action == 'attack_light':
            self.press_key('a')
        elif action == 'attack_medium':
            self.press_key('s')
        elif action == 'attack_heavy':
            self.press_key('d')
        elif action == 'move_forward':
            self.hold_key('right', 0.3)
        elif action == 'move_backward':
            self.hold_key('left', 0.3)
        elif action == 'jump':
            self.press_key('up')
        elif action == 'crouch':
            self.hold_key('down', 0.2)
        elif action == 'special_move':
            self.press_key('down')
            time.sleep(0.05)
            self.press_key('right')
            time.sleep(0.05)
            self.press_key('a')
        elif action == 'block':
            self.hold_key('left', 0.5)
        elif action == 'dash_forward':
            self.press_key('right')
            time.sleep(0.05)
            self.press_key('right')
        elif action == 'dash_backward':
            self.press_key('left')
            time.sleep(0.05)
            self.press_key('left')

    def play_match(self, duration=60):
        start_time = time.time()
        screenshot_interval = 10
        last_screenshot = time.time()

        while time.time() - start_time < duration:
            self.perform_random_action()

            if time.time() - last_screenshot >= screenshot_interval:
                elapsed = int(time.time() - start_time)
                self.take_screenshot(f"fight_{elapsed}s")
                last_screenshot = time.time()

            time.sleep(random.uniform(0.1, 0.3))

        self.take_screenshot("match_end")

    def play_silent_session(self):
        # Démarrer
        self.start_game()
        self.navigate_to_vs()

        # Sélection
        self.take_screenshot("selection_p1")
        self.select_random_character()
        self.take_screenshot("selection_p2")
        self.select_random_character()

        # VS Screen
        time.sleep(2)
        self.take_screenshot("vs_screen")
        time.sleep(3)

        # Combat
        self.play_match(duration=60)

        # Fin
        time.sleep(3)
        self.take_screenshot("results")

        for _ in range(5):
            self.press_key('return', 0.5)

def main():
    game_dir = r"D:\KOF Ultimate Online kofuo Online kofuo kofuo Online kofuo"
    ai = SilentAIPlayer(game_dir)

    # Silence total
    sys.stdout = SilentOutput()
    sys.stderr = SilentOutput()

    ai.play_silent_session()

if __name__ == '__main__':
    main()
