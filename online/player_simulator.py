#!/usr/bin/env python3
"""
KOF ULTIMATE ONLINE - ADVANCED PLAYER SIMULATOR
================================================
Simulates realistic player behavior:
- Menu navigation
- Profile browsing
- Leaderboard checking
- 1v1 match searching
- Character selection
- Chat interactions
"""

import asyncio
import json
import random
import time
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(r"D:\KOF Ultimate Online")
SAVE_DIR = BASE_DIR / "save"

# Character roster
CHARACTERS = [
    "Kyo", "Iori", "Terry", "Ryo", "Athena", "Mai", "King", "Leona",
    "K'", "Maxima", "Whip", "Vanessa", "Blue Mary", "Rock", "Geese",
    "Rugal", "Orochi", "Ash", "Elisabeth", "Shen", "Duo Lon", "Shermie",
    "Chris", "Yashiro", "Kula", "Angel", "Nameless", "Chizuru", "Mature",
    "Vice", "Yamazaki", "Billy", "Heidern", "Clark", "Ralf", "Shingo"
]

# Player personalities
PERSONALITIES = {
    "aggressive": {"queue_chance": 0.4, "chat_chance": 0.3, "browse_chance": 0.2},
    "casual": {"queue_chance": 0.2, "chat_chance": 0.4, "browse_chance": 0.3},
    "competitive": {"queue_chance": 0.5, "chat_chance": 0.1, "browse_chance": 0.4},
    "social": {"queue_chance": 0.1, "chat_chance": 0.5, "browse_chance": 0.4},
    "lurker": {"queue_chance": 0.1, "chat_chance": 0.05, "browse_chance": 0.6},
}

# Chat messages by context
CHAT_MESSAGES = {
    "greeting": [
        "Hey everyone!", "What's up!", "Who's ready to fight?",
        "Let's go!", "GGs in advance!", "Anyone here?", "yo"
    ],
    "looking_for_match": [
        "Anyone up for ranked?", "Looking for 1v1", "Who wants to spar?",
        "FT10 anyone?", "Need practice partner", "Ranked queue is dead...",
        "Let's run some sets!", "Who's next?", "Challenge me!"
    ],
    "post_match": [
        "GGs!", "Good games!", "That was close!", "Nice combos!",
        "Rematch?", "Well played!", "I need more practice...",
        "My execution was off", "Lag?", "One more?"
    ],
    "character_talk": [
        "Kyo mains rise up!", "Iori is broken", "Nerf Rugal pls",
        "Terry is honest", "Mai combos are sick", "K' gang",
        "Ash takes skill actually", "Geese players are scary"
    ],
    "general": [
        "This game is hype", "Love this community", "When's the next tourney?",
        "Anyone streaming?", "Frame data check", "What's the meta rn?"
    ]
}

class SimulatedPlayer:
    def __init__(self, username: str, elo: int):
        self.username = username
        self.elo = elo
        self.personality = random.choice(list(PERSONALITIES.keys()))
        self.main_char = random.choice(CHARACTERS)
        self.state = "idle"  # idle, in_menu, browsing, queuing, in_match
        self.current_menu = "main"
        self.last_action_time = time.time()
        self.session_matches = 0
        self.mood = random.choice(["happy", "focused", "tilted", "chill"])

    def get_action_delay(self) -> float:
        """Get delay before next action based on personality."""
        base_delay = random.uniform(2, 8)
        if self.personality == "aggressive":
            return base_delay * 0.7
        elif self.personality == "lurker":
            return base_delay * 1.5
        return base_delay


class AdvancedSimulator:
    def __init__(self):
        self.players = {}
        self.activity_log = []
        self.match_queue_ranked = []
        self.match_queue_casual = []
        self.active_matches = []
        self.leaderboard = []
        self.running = True
        self.total_matches = 0
        self.load_leaderboard()

    def load_leaderboard(self):
        """Load current leaderboard."""
        try:
            with open(SAVE_DIR / "leaderboard.json", 'r') as f:
                data = json.load(f)
                self.leaderboard = data.get("rankings", [])
        except:
            self.leaderboard = []

    def log(self, player: str, action: str, details: str = ""):
        """Log player activity."""
        entry = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "player": player,
            "action": action,
            "details": details
        }
        self.activity_log.append(entry)
        if len(self.activity_log) > 200:
            self.activity_log.pop(0)
        print(f"[{entry['time']}] {player}: {action} {details}")

    def simulate_menu_navigation(self, player: SimulatedPlayer):
        """Simulate player navigating menus."""
        menus = ["main", "online", "arcade", "versus", "training", "options"]
        online_submenus = ["host", "join", "lobby", "leaderboard", "profile"]

        if player.current_menu == "main":
            # Go to online menu
            player.current_menu = "online"
            self.log(player.username, "MENU", "Entered ONLINE menu")
        elif player.current_menu == "online":
            action = random.choice(online_submenus + ["back"])
            if action == "back":
                player.current_menu = "main"
                self.log(player.username, "MENU", "Returned to main menu")
            elif action == "leaderboard":
                self.log(player.username, "VIEW_LEADERBOARD", "Checking world rankings")
                # Simulate viewing top players
                if self.leaderboard:
                    top3 = self.leaderboard[:3]
                    names = ", ".join([p.get("username", "???") for p in top3])
                    self.log(player.username, "LEADERBOARD", f"Top 3: {names}")
            elif action == "profile":
                self.log(player.username, "VIEW_PROFILE", f"Viewing own profile (ELO: {player.elo})")
            elif action == "lobby":
                self.log(player.username, "ENTER_LOBBY", "Entered live lobby")
                player.state = "browsing"
            else:
                player.current_menu = action
                self.log(player.username, "MENU", f"Selected {action.upper()}")

    def simulate_profile_browsing(self, player: SimulatedPlayer):
        """Simulate player browsing other profiles."""
        if self.leaderboard:
            target = random.choice(self.leaderboard[:20])
            target_name = target.get("username", "Unknown")
            target_elo = target.get("elo", 1200)
            target_wins = target.get("wins", 0)
            target_losses = target.get("losses", 0)
            self.log(player.username, "VIEW_PROFILE",
                    f"Viewed {target_name}'s profile (ELO:{target_elo} {target_wins}W/{target_losses}L)")

    def simulate_match_search(self, player: SimulatedPlayer):
        """Simulate player searching for a match."""
        match_type = random.choice(["ranked", "casual"])

        if match_type == "ranked":
            if player.username not in self.match_queue_ranked:
                self.match_queue_ranked.append(player.username)
                self.log(player.username, "QUEUE_RANKED", f"Searching for ranked match (ELO: {player.elo})")
                player.state = "queuing"
        else:
            if player.username not in self.match_queue_casual:
                self.match_queue_casual.append(player.username)
                self.log(player.username, "QUEUE_CASUAL", "Searching for casual match")
                player.state = "queuing"

    def simulate_chat(self, player: SimulatedPlayer):
        """Simulate player chatting."""
        context = random.choice(list(CHAT_MESSAGES.keys()))
        message = random.choice(CHAT_MESSAGES[context])
        self.log(player.username, "CHAT", f'"{message}"')

    def process_match_queues(self):
        """Match players in queues."""
        # Ranked matching (ELO-based)
        if len(self.match_queue_ranked) >= 2:
            # Sort by ELO and match closest
            queue_with_elo = [(p, self.players[p].elo) for p in self.match_queue_ranked if p in self.players]
            queue_with_elo.sort(key=lambda x: x[1])

            if len(queue_with_elo) >= 2:
                p1_name = queue_with_elo[0][0]
                p2_name = queue_with_elo[1][0]

                self.match_queue_ranked.remove(p1_name)
                self.match_queue_ranked.remove(p2_name)

                self.start_match(p1_name, p2_name, "RANKED")

        # Casual matching (random)
        if len(self.match_queue_casual) >= 2:
            p1_name = self.match_queue_casual.pop(0)
            p2_name = self.match_queue_casual.pop(random.randint(0, len(self.match_queue_casual)-1) if self.match_queue_casual else 0)
            if p2_name:
                self.start_match(p1_name, p2_name, "CASUAL")

    def start_match(self, p1_name: str, p2_name: str, match_type: str):
        """Start a match between two players."""
        p1 = self.players.get(p1_name)
        p2 = self.players.get(p2_name)

        if not p1 or not p2:
            return

        p1_char = p1.main_char if random.random() > 0.3 else random.choice(CHARACTERS)
        p2_char = p2.main_char if random.random() > 0.3 else random.choice(CHARACTERS)

        match = {
            "p1": p1_name,
            "p2": p2_name,
            "p1_char": p1_char,
            "p2_char": p2_char,
            "type": match_type,
            "start_time": time.time(),
            "duration": random.randint(45, 180)
        }

        self.active_matches.append(match)
        p1.state = "in_match"
        p2.state = "in_match"

        self.log(p1_name, "MATCH_FOUND", f"vs {p2_name} ({p2_char}) [{match_type}]")
        self.log(p2_name, "MATCH_FOUND", f"vs {p1_name} ({p1_char}) [{match_type}]")

    def process_matches(self):
        """Process ongoing matches."""
        completed = []
        for match in self.active_matches:
            if time.time() - match["start_time"] >= match["duration"]:
                completed.append(match)

        for match in completed:
            self.active_matches.remove(match)
            self.complete_match(match)

    def complete_match(self, match: dict):
        """Complete a match and determine winner."""
        p1 = self.players.get(match["p1"])
        p2 = self.players.get(match["p2"])

        if not p1 or not p2:
            return

        # Determine winner based on ELO
        elo_diff = p1.elo - p2.elo
        p1_win_prob = 1 / (1 + 10 ** (-elo_diff / 400))

        if random.random() < p1_win_prob:
            winner, loser = p1, p2
        else:
            winner, loser = p2, p1

        winner_rounds = 2
        loser_rounds = random.randint(0, 1)

        self.total_matches += 1
        winner.session_matches += 1
        loser.session_matches += 1

        # Update states
        p1.state = "idle"
        p2.state = "idle"

        # Log result
        elo_change = random.randint(8, 25) if match["type"] == "RANKED" else 0
        self.log(winner.username, "MATCH_WIN",
                f"defeated {loser.username} ({winner_rounds}-{loser_rounds})" +
                (f" [+{elo_change} ELO]" if elo_change else " [CASUAL]"))

        # Post-match chat
        if random.random() > 0.5:
            msg = random.choice(CHAT_MESSAGES["post_match"])
            self.log(winner.username, "CHAT", f'"{msg}"')

    def player_tick(self, player: SimulatedPlayer):
        """Process one tick for a player."""
        if time.time() - player.last_action_time < player.get_action_delay():
            return

        player.last_action_time = time.time()
        prefs = PERSONALITIES[player.personality]

        if player.state == "in_match":
            return  # Don't do anything while in match

        if player.state == "queuing":
            # Maybe cancel queue
            if random.random() < 0.05:
                if player.username in self.match_queue_ranked:
                    self.match_queue_ranked.remove(player.username)
                if player.username in self.match_queue_casual:
                    self.match_queue_casual.remove(player.username)
                player.state = "idle"
                self.log(player.username, "CANCEL_QUEUE", "Cancelled matchmaking")
            return

        # Choose action based on personality
        roll = random.random()

        if roll < prefs["queue_chance"]:
            self.simulate_match_search(player)
        elif roll < prefs["queue_chance"] + prefs["chat_chance"]:
            self.simulate_chat(player)
        elif roll < prefs["queue_chance"] + prefs["chat_chance"] + prefs["browse_chance"]:
            if random.random() > 0.5:
                self.simulate_profile_browsing(player)
            else:
                self.simulate_menu_navigation(player)
        else:
            # Random idle action
            actions = [
                lambda: self.log(player.username, "IDLE", "Watching matches..."),
                lambda: self.log(player.username, "IDLE", "Practicing combos in training..."),
                lambda: self.log(player.username, "VIEW_LEADERBOARD", "Refreshing rankings..."),
            ]
            random.choice(actions)()

    def save_status(self):
        """Save current simulation status."""
        status = {
            "players_online": len(self.players),
            "queue_ranked": len(self.match_queue_ranked),
            "queue_casual": len(self.match_queue_casual),
            "active_matches": len(self.active_matches),
            "total_matches": self.total_matches,
            "recent_activity": [
                {"timestamp": a["time"], "type": a["action"].lower(),
                 "message": f"{a['player']}: {a['action']} {a['details']}"}
                for a in self.activity_log[-30:]
            ],
            "last_updated": datetime.now().isoformat()
        }

        with open(SAVE_DIR / "simulator_status.json", 'w') as f:
            json.dump(status, f, indent=2)

    async def run(self, num_players: int = 25):
        """Run the advanced simulation."""
        print("=" * 60)
        print("  KOF ULTIMATE ONLINE - ADVANCED PLAYER SIMULATOR")
        print("=" * 60)

        # Load existing players from leaderboard
        self.load_leaderboard()

        # Create simulated players
        for entry in self.leaderboard[:num_players]:
            username = entry.get("username", f"Player_{len(self.players)}")
            elo = entry.get("elo", 1200)
            self.players[username] = SimulatedPlayer(username, elo)

        print(f"Loaded {len(self.players)} players")
        print("=" * 60)

        tick = 0
        while self.running:
            try:
                # Process each player
                for player in list(self.players.values()):
                    self.player_tick(player)

                # Process queues and matches
                self.process_match_queues()
                self.process_matches()

                # Save status periodically
                if tick % 10 == 0:
                    self.save_status()

                # Status update
                if tick % 30 == 0 and tick > 0:
                    print(f"\n--- STATUS: {len(self.players)} online | "
                          f"{len(self.active_matches)} matches | "
                          f"{self.total_matches} total ---\n")

                tick += 1
                await asyncio.sleep(1)

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")

        print("\nSimulator stopped.")
        self.save_status()


async def main():
    simulator = AdvancedSimulator()
    await simulator.run(25)


if __name__ == "__main__":
    print("\nStarting Advanced Player Simulator...")
    asyncio.run(main())
