#!/usr/bin/env python3
"""
KOF ULTIMATE ONLINE - MATCHMAKING SERVER
=========================================
Real-time matchmaking server with:
- WebSocket connections
- Player queue management
- Match simulation
- Live activity feed
- Automated tournaments
"""

import asyncio
import json
import random
import time
import os
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading

# Import our online system
import sys
sys.path.insert(0, str(Path(__file__).parent))
from kof_online_system import OnlineSystem, CHARACTERS, AI_PLAYERS

# Paths
BASE_DIR = Path(r"D:\KOF Ultimate Online")
SAVE_DIR = BASE_DIR / "save"

class MatchmakingServer:
    """Real-time matchmaking and simulation server."""

    def __init__(self):
        self.online_system = OnlineSystem()
        self.queue_ranked = []
        self.queue_casual = []
        self.active_matches = []
        self.activity_log = []
        self.running = True
        self.match_count = 0
        self.players_online = set()

        # Simulated online players
        self.simulated_players = list(AI_PLAYERS)[:20]
        for player in self.simulated_players:
            self.players_online.add(player)

    def log_activity(self, message: str, activity_type: str = "info"):
        """Log an activity event."""
        entry = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "type": activity_type,
            "message": message
        }
        self.activity_log.append(entry)
        # Keep last 100 entries
        if len(self.activity_log) > 100:
            self.activity_log.pop(0)
        print(f"[{entry['timestamp']}] [{activity_type.upper()}] {message}")

    def simulate_player_activity(self):
        """Simulate random player activities."""
        activities = [
            ("join", lambda: self.player_joins()),
            ("leave", lambda: self.player_leaves()),
            ("queue_ranked", lambda: self.player_queues_ranked()),
            ("queue_casual", lambda: self.player_queues_casual()),
            ("chat", lambda: self.player_chats()),
            ("view_profile", lambda: self.player_views_profile()),
            ("view_leaderboard", lambda: self.log_activity(f"{random.choice(list(self.players_online))} viewed the leaderboard", "browse")),
        ]

        # Pick random activity
        activity_name, activity_func = random.choice(activities)
        try:
            activity_func()
        except Exception as e:
            pass

    def player_joins(self):
        """Simulate a player joining."""
        available = [p for p in AI_PLAYERS if p not in self.players_online]
        if available and len(self.players_online) < 50:
            player = random.choice(available)
            self.players_online.add(player)
            profile = self.online_system.get_or_create_player(player)
            self.log_activity(f"{player} joined the lobby (ELO: {profile.elo})", "join")

    def player_leaves(self):
        """Simulate a player leaving."""
        if len(self.players_online) > 5:
            player = random.choice(list(self.players_online))
            self.players_online.discard(player)
            # Remove from queues
            if player in self.queue_ranked:
                self.queue_ranked.remove(player)
            if player in self.queue_casual:
                self.queue_casual.remove(player)
            self.log_activity(f"{player} left the lobby", "leave")

    def player_queues_ranked(self):
        """Simulate a player joining ranked queue."""
        available = [p for p in self.players_online if p not in self.queue_ranked and p not in self.queue_casual]
        if available:
            player = random.choice(available)
            self.queue_ranked.append(player)
            profile = self.online_system.get_or_create_player(player)
            self.log_activity(f"{player} joined RANKED queue (ELO: {profile.elo})", "queue")

    def player_queues_casual(self):
        """Simulate a player joining casual queue."""
        available = [p for p in self.players_online if p not in self.queue_ranked and p not in self.queue_casual]
        if available:
            player = random.choice(available)
            self.queue_casual.append(player)
            self.log_activity(f"{player} joined CASUAL queue", "queue")

    def player_chats(self):
        """Simulate a player chatting."""
        if self.players_online:
            player = random.choice(list(self.players_online))
            messages = [
                "GGs everyone!",
                "Anyone up for a ft10?",
                "Looking for sparring partner",
                "Nice combos!",
                "Let's go!",
                "Who wants to run some sets?",
                "My Kyo is unbeatable!",
                "Iori mains where you at?",
                "Training hard today",
                "That was close!",
            ]
            msg = random.choice(messages)
            self.log_activity(f"[CHAT] {player}: {msg}", "chat")

    def player_views_profile(self):
        """Simulate a player viewing another's profile."""
        if len(self.players_online) >= 2:
            players = list(self.players_online)
            viewer = random.choice(players)
            viewed = random.choice([p for p in players if p != viewer])
            self.log_activity(f"{viewer} viewed {viewed}'s profile", "browse")

    def process_queues(self):
        """Process matchmaking queues and create matches."""
        # Ranked matchmaking (ELO-based)
        if len(self.queue_ranked) >= 2:
            # Sort by ELO
            self.queue_ranked.sort(key=lambda p: self.online_system.get_or_create_player(p).elo)

            # Match closest ELO players
            p1 = self.queue_ranked.pop(0)
            p2 = self.queue_ranked.pop(0)

            self.start_match(p1, p2, "RANKED")

        # Casual matchmaking (random)
        if len(self.queue_casual) >= 2:
            p1 = self.queue_casual.pop(0)
            p2 = self.queue_casual.pop(random.randint(0, len(self.queue_casual) - 1) if self.queue_casual else 0)
            if p2:
                self.start_match(p1, p2, "CASUAL")

    def start_match(self, player1: str, player2: str, match_type: str):
        """Start a match between two players."""
        p1_char = random.choice(CHARACTERS)
        p2_char = random.choice(CHARACTERS)

        match = {
            "id": f"M{int(time.time())}_{random.randint(100,999)}",
            "player1": player1,
            "player2": player2,
            "p1_char": p1_char,
            "p2_char": p2_char,
            "type": match_type,
            "start_time": time.time(),
            "duration": random.randint(60, 180),  # 1-3 minutes
            "rounds": []
        }

        self.active_matches.append(match)
        self.match_count += 1

        p1_profile = self.online_system.get_or_create_player(player1)
        p2_profile = self.online_system.get_or_create_player(player2)

        self.log_activity(
            f"MATCH STARTED: {player1} ({p1_char}, ELO:{p1_profile.elo}) vs {player2} ({p2_char}, ELO:{p2_profile.elo}) [{match_type}]",
            "match_start"
        )

    def process_matches(self):
        """Process active matches and determine winners."""
        current_time = time.time()
        completed = []

        for match in self.active_matches:
            if current_time - match["start_time"] >= match["duration"]:
                completed.append(match)

        for match in completed:
            self.active_matches.remove(match)
            self.complete_match(match)

    def complete_match(self, match: dict):
        """Complete a match and record results."""
        p1 = match["player1"]
        p2 = match["player2"]

        # Determine winner based on ELO probability
        p1_profile = self.online_system.get_or_create_player(p1)
        p2_profile = self.online_system.get_or_create_player(p2)

        win_prob = 1 / (1 + 10 ** ((p2_profile.elo - p1_profile.elo) / 400))
        winner = p1 if random.random() < win_prob else p2
        loser = p2 if winner == p1 else p1

        # Random round scores
        winner_rounds = 2
        loser_rounds = random.randint(0, 1)

        p1_rounds = winner_rounds if winner == p1 else loser_rounds
        p2_rounds = winner_rounds if winner == p2 else loser_rounds

        # Record the match
        if match["type"] == "RANKED":
            result = self.online_system.record_match(
                p1, p2, winner,
                match["p1_char"], match["p2_char"],
                p1_rounds, p2_rounds
            )

            elo_change = result.elo_change_p1 if winner == p1 else result.elo_change_p2
            self.log_activity(
                f"MATCH COMPLETE: {winner} defeats {loser} ({winner_rounds}-{loser_rounds}) [+{abs(elo_change)} ELO]",
                "match_end"
            )
        else:
            self.log_activity(
                f"MATCH COMPLETE: {winner} defeats {loser} ({winner_rounds}-{loser_rounds}) [CASUAL]",
                "match_end"
            )

        # Return players to online pool
        self.players_online.add(p1)
        self.players_online.add(p2)

    def get_status(self) -> dict:
        """Get current server status."""
        return {
            "players_online": len(self.players_online),
            "queue_ranked": len(self.queue_ranked),
            "queue_casual": len(self.queue_casual),
            "active_matches": len(self.active_matches),
            "total_matches": self.match_count,
            "total_players": len(self.online_system.players),
            "recent_activity": self.activity_log[-20:],
            "leaderboard": self.online_system.get_leaderboard(10)
        }

    def save_status(self):
        """Save current status to file."""
        status = self.get_status()
        status["last_updated"] = datetime.now().isoformat()

        filepath = SAVE_DIR / "server_status.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(status, f, indent=2, ensure_ascii=False)

    async def run(self):
        """Main server loop."""
        print("=" * 60)
        print("  KOF ULTIMATE ONLINE - MATCHMAKING SERVER")
        print("=" * 60)
        print(f"  Players online: {len(self.players_online)}")
        print(f"  Total registered: {len(self.online_system.players)}")
        print("=" * 60)
        print()

        self.log_activity("Server started", "system")

        tick = 0
        while self.running:
            try:
                # Activity simulation (every 2-5 seconds)
                if tick % random.randint(2, 5) == 0:
                    self.simulate_player_activity()

                # Queue processing (every second)
                self.process_queues()

                # Match processing (every second)
                self.process_matches()

                # Save status (every 10 seconds)
                if tick % 10 == 0:
                    self.save_status()
                    self.online_system.save_leaderboard()

                # Display status (every 30 seconds)
                if tick % 30 == 0 and tick > 0:
                    status = self.get_status()
                    print(f"\n--- STATUS: {status['players_online']} online | {status['active_matches']} matches | {status['total_matches']} total ---\n")

                tick += 1
                await asyncio.sleep(1)

            except KeyboardInterrupt:
                self.running = False
                break
            except Exception as e:
                print(f"Error: {e}")

        print("\nServer shutting down...")
        self.save_status()


def run_http_server():
    """Run HTTP server for the lobby page."""
    os.chdir(str(BASE_DIR / "online"))
    handler = SimpleHTTPRequestHandler
    server = HTTPServer(('localhost', 8080), handler)
    print("[HTTP] Lobby server running at http://localhost:8080/lobby.html")
    server.serve_forever()


async def main():
    """Main entry point."""
    # Start HTTP server in background
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()

    # Run matchmaking server
    server = MatchmakingServer()
    await server.run()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  STARTING KOF ULTIMATE ONLINE SERVER")
    print("=" * 60 + "\n")

    asyncio.run(main())
