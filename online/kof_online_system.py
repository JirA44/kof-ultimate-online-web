#!/usr/bin/env python3
"""
KOF Ultimate Online - Battle.net Style Online System
=====================================================
Features:
- Player profiles with stats
- ELO ranking system
- Match history
- Leaderboards
- Matchmaking simulation
- AI player simulation
"""

import json
import os
import random
import time
from datetime import datetime
from pathlib import Path

# Paths
BASE_DIR = Path(r"D:\KOF Ultimate Online")
SAVE_DIR = BASE_DIR / "save"
PROFILES_DIR = SAVE_DIR / "profiles"
MATCHES_DIR = SAVE_DIR / "matches"
ONLINE_DIR = BASE_DIR / "online"

# Create directories
PROFILES_DIR.mkdir(parents=True, exist_ok=True)
MATCHES_DIR.mkdir(parents=True, exist_ok=True)

# Default ELO
DEFAULT_ELO = 1200
K_FACTOR = 32

# Character roster for simulation
CHARACTERS = [
    "Kyo", "Iori", "Terry", "Ryo", "Robert", "Athena", "Kensou", "Leona",
    "Ralf", "Clark", "Mai", "King", "Yuri", "K'", "Maxima", "Whip",
    "Vanessa", "Ramon", "Angel", "Kula", "Ash", "Elisabeth", "Shen", "Duo Lon",
    "Benimaru", "Goro", "Shingo", "Chizuru", "Vice", "Mature", "Yamazaki",
    "Billy", "Blue Mary", "Geese", "Rugal", "Orochi", "Shermie", "Chris", "Yashiro"
]

# AI Player names for simulation
AI_PLAYERS = [
    "DragonFist_99", "ShadowKing_X", "NeoGeo_Master", "KOF_Legend",
    "FatalFury_Pro", "SNK_Champion", "Arcade_Warrior", "Combo_Breaker",
    "Perfect_KO", "Rush_Down_King", "Zoner_Elite", "Grappler_God",
    "Mix_Up_Master", "Frame_Perfect", "Tournament_Ace", "Online_Warrior",
    "Ranked_Slayer", "EVO_Ready", "FGC_Veteran", "Button_Masher_X",
    "Pro_Player_One", "Casual_Fighter", "Training_Mode", "Salt_Shaker",
    "Rage_Quitter_0", "GG_EZ_Player", "Hype_Beast_99", "Clutch_King",
    "Comeback_Kid", "First_To_10", "Money_Match", "Stream_Monster"
]


class PlayerProfile:
    """Player profile with stats and history."""

    def __init__(self, username: str):
        self.username = username
        self.elo = DEFAULT_ELO
        self.wins = 0
        self.losses = 0
        self.win_streak = 0
        self.max_win_streak = 0
        self.main_characters = []
        self.match_history = []
        self.created_at = datetime.now().isoformat()
        self.last_online = datetime.now().isoformat()
        self.title = "Rookie"
        self.country = "Unknown"
        self.total_matches = 0
        self.total_rounds_won = 0
        self.total_rounds_lost = 0
        self.perfect_rounds = 0

    def to_dict(self) -> dict:
        return {
            "username": self.username,
            "elo": self.elo,
            "wins": self.wins,
            "losses": self.losses,
            "win_streak": self.win_streak,
            "max_win_streak": self.max_win_streak,
            "main_characters": self.main_characters,
            "match_history": self.match_history[-50:],  # Keep last 50
            "created_at": self.created_at,
            "last_online": self.last_online,
            "title": self.title,
            "country": self.country,
            "total_matches": self.total_matches,
            "total_rounds_won": self.total_rounds_won,
            "total_rounds_lost": self.total_rounds_lost,
            "perfect_rounds": self.perfect_rounds
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'PlayerProfile':
        player = cls(data["username"])
        player.elo = data.get("elo", DEFAULT_ELO)
        player.wins = data.get("wins", 0)
        player.losses = data.get("losses", 0)
        player.win_streak = data.get("win_streak", 0)
        player.max_win_streak = data.get("max_win_streak", 0)
        player.main_characters = data.get("main_characters", [])
        player.match_history = data.get("match_history", [])
        player.created_at = data.get("created_at", datetime.now().isoformat())
        player.last_online = data.get("last_online", datetime.now().isoformat())
        player.title = data.get("title", "Rookie")
        player.country = data.get("country", "Unknown")
        player.total_matches = data.get("total_matches", 0)
        player.total_rounds_won = data.get("total_rounds_won", 0)
        player.total_rounds_lost = data.get("total_rounds_lost", 0)
        player.perfect_rounds = data.get("perfect_rounds", 0)
        return player

    def get_winrate(self) -> float:
        total = self.wins + self.losses
        return (self.wins / total * 100) if total > 0 else 0.0

    def get_title_from_elo(self) -> str:
        if self.elo >= 2400: return "Grand Master"
        if self.elo >= 2200: return "Master"
        if self.elo >= 2000: return "Diamond"
        if self.elo >= 1800: return "Platinum"
        if self.elo >= 1600: return "Gold"
        if self.elo >= 1400: return "Silver"
        if self.elo >= 1200: return "Bronze"
        return "Rookie"

    def update_title(self):
        self.title = self.get_title_from_elo()

    def save(self):
        filepath = PROFILES_DIR / f"{self.username}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, username: str) -> 'PlayerProfile':
        filepath = PROFILES_DIR / f"{username}.json"
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return cls.from_dict(json.load(f))
        return cls(username)


class ELOSystem:
    """ELO rating calculation system."""

    @staticmethod
    def expected_score(elo_a: int, elo_b: int) -> float:
        return 1 / (1 + 10 ** ((elo_b - elo_a) / 400))

    @staticmethod
    def calculate_new_elo(winner_elo: int, loser_elo: int) -> tuple:
        expected_winner = ELOSystem.expected_score(winner_elo, loser_elo)
        expected_loser = ELOSystem.expected_score(loser_elo, winner_elo)

        new_winner_elo = round(winner_elo + K_FACTOR * (1 - expected_winner))
        new_loser_elo = round(loser_elo + K_FACTOR * (0 - expected_loser))

        # Minimum ELO is 100
        new_loser_elo = max(100, new_loser_elo)

        return new_winner_elo, new_loser_elo


class Match:
    """Represents a match between two players."""

    def __init__(self, player1: str, player2: str):
        self.match_id = f"{int(time.time())}_{random.randint(1000, 9999)}"
        self.player1 = player1
        self.player2 = player2
        self.player1_char = ""
        self.player2_char = ""
        self.winner = None
        self.rounds = []  # List of round results
        self.player1_rounds = 0
        self.player2_rounds = 0
        self.timestamp = datetime.now().isoformat()
        self.duration_seconds = 0
        self.elo_change_p1 = 0
        self.elo_change_p2 = 0

    def to_dict(self) -> dict:
        return {
            "match_id": self.match_id,
            "player1": self.player1,
            "player2": self.player2,
            "player1_char": self.player1_char,
            "player2_char": self.player2_char,
            "winner": self.winner,
            "rounds": self.rounds,
            "player1_rounds": self.player1_rounds,
            "player2_rounds": self.player2_rounds,
            "timestamp": self.timestamp,
            "duration_seconds": self.duration_seconds,
            "elo_change_p1": self.elo_change_p1,
            "elo_change_p2": self.elo_change_p2
        }

    def save(self):
        filepath = MATCHES_DIR / f"{self.match_id}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)


class OnlineSystem:
    """Main online system manager."""

    def __init__(self):
        self.players = {}  # username -> PlayerProfile
        self.load_all_profiles()
        self.leaderboard_cache = []
        self.update_leaderboard()

    def load_all_profiles(self):
        """Load all player profiles from disk."""
        for filepath in PROFILES_DIR.glob("*.json"):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    player = PlayerProfile.from_dict(data)
                    self.players[player.username] = player
            except Exception as e:
                print(f"Error loading {filepath}: {e}")

    def get_or_create_player(self, username: str) -> PlayerProfile:
        """Get existing player or create new one."""
        if username not in self.players:
            self.players[username] = PlayerProfile(username)
            self.players[username].save()
        return self.players[username]

    def update_leaderboard(self):
        """Update the cached leaderboard."""
        self.leaderboard_cache = sorted(
            self.players.values(),
            key=lambda p: p.elo,
            reverse=True
        )

    def get_leaderboard(self, top_n: int = 100) -> list:
        """Get top N players."""
        return [
            {
                "rank": i + 1,
                "username": p.username,
                "elo": p.elo,
                "title": p.title,
                "wins": p.wins,
                "losses": p.losses,
                "winrate": p.get_winrate(),
                "country": p.country
            }
            for i, p in enumerate(self.leaderboard_cache[:top_n])
        ]

    def get_player_rank(self, username: str) -> int:
        """Get player's current rank."""
        for i, p in enumerate(self.leaderboard_cache):
            if p.username == username:
                return i + 1
        return -1

    def record_match(self, player1_name: str, player2_name: str,
                     winner_name: str, p1_char: str, p2_char: str,
                     p1_rounds: int, p2_rounds: int, rounds_detail: list = None):
        """Record a match result and update ELO."""

        player1 = self.get_or_create_player(player1_name)
        player2 = self.get_or_create_player(player2_name)

        # Create match record
        match = Match(player1_name, player2_name)
        match.player1_char = p1_char
        match.player2_char = p2_char
        match.winner = winner_name
        match.player1_rounds = p1_rounds
        match.player2_rounds = p2_rounds
        match.rounds = rounds_detail or []

        # Calculate ELO changes
        if winner_name == player1_name:
            new_p1_elo, new_p2_elo = ELOSystem.calculate_new_elo(player1.elo, player2.elo)
            match.elo_change_p1 = new_p1_elo - player1.elo
            match.elo_change_p2 = new_p2_elo - player2.elo

            player1.wins += 1
            player1.win_streak += 1
            player1.max_win_streak = max(player1.max_win_streak, player1.win_streak)
            player2.losses += 1
            player2.win_streak = 0
        else:
            new_p2_elo, new_p1_elo = ELOSystem.calculate_new_elo(player2.elo, player1.elo)
            match.elo_change_p1 = new_p1_elo - player1.elo
            match.elo_change_p2 = new_p2_elo - player2.elo

            player2.wins += 1
            player2.win_streak += 1
            player2.max_win_streak = max(player2.max_win_streak, player2.win_streak)
            player1.losses += 1
            player1.win_streak = 0

        # Update ELO
        player1.elo = new_p1_elo
        player2.elo = new_p2_elo

        # Update stats
        player1.total_matches += 1
        player2.total_matches += 1
        player1.total_rounds_won += p1_rounds
        player1.total_rounds_lost += p2_rounds
        player2.total_rounds_won += p2_rounds
        player2.total_rounds_lost += p1_rounds

        # Update main characters
        if p1_char and p1_char not in player1.main_characters:
            player1.main_characters.append(p1_char)
            player1.main_characters = player1.main_characters[-5:]  # Keep last 5
        if p2_char and p2_char not in player2.main_characters:
            player2.main_characters.append(p2_char)
            player2.main_characters = player2.main_characters[-5:]

        # Update titles
        player1.update_title()
        player2.update_title()

        # Update last online
        player1.last_online = datetime.now().isoformat()
        player2.last_online = datetime.now().isoformat()

        # Add to match history
        match_summary = {
            "match_id": match.match_id,
            "opponent": player2_name,
            "result": "WIN" if winner_name == player1_name else "LOSS",
            "elo_change": match.elo_change_p1,
            "my_char": p1_char,
            "opp_char": p2_char,
            "score": f"{p1_rounds}-{p2_rounds}",
            "timestamp": match.timestamp
        }
        player1.match_history.append(match_summary)

        match_summary2 = {
            "match_id": match.match_id,
            "opponent": player1_name,
            "result": "WIN" if winner_name == player2_name else "LOSS",
            "elo_change": match.elo_change_p2,
            "my_char": p2_char,
            "opp_char": p1_char,
            "score": f"{p2_rounds}-{p1_rounds}",
            "timestamp": match.timestamp
        }
        player2.match_history.append(match_summary2)

        # Save everything
        player1.save()
        player2.save()
        match.save()

        # Update leaderboard
        self.update_leaderboard()

        return match

    def simulate_match(self, player1_name: str = None, player2_name: str = None) -> Match:
        """Simulate a random match between two players."""

        if player1_name is None:
            player1_name = random.choice(AI_PLAYERS)
        if player2_name is None:
            player2_name = random.choice([p for p in AI_PLAYERS if p != player1_name])

        p1 = self.get_or_create_player(player1_name)
        p2 = self.get_or_create_player(player2_name)

        # Pick characters
        p1_char = random.choice(CHARACTERS)
        p2_char = random.choice(CHARACTERS)

        # Simulate rounds (best of 3)
        p1_rounds = 0
        p2_rounds = 0
        rounds = []

        while p1_rounds < 2 and p2_rounds < 2:
            # Win probability based on ELO
            p1_win_prob = ELOSystem.expected_score(p1.elo, p2.elo)

            if random.random() < p1_win_prob:
                p1_rounds += 1
                rounds.append({"winner": player1_name, "perfect": random.random() < 0.05})
            else:
                p2_rounds += 1
                rounds.append({"winner": player2_name, "perfect": random.random() < 0.05})

        winner = player1_name if p1_rounds > p2_rounds else player2_name

        return self.record_match(
            player1_name, player2_name, winner,
            p1_char, p2_char, p1_rounds, p2_rounds, rounds
        )

    def simulate_tournament(self, num_matches: int = 50):
        """Simulate multiple matches to populate the system."""
        print(f"Simulating {num_matches} matches...")

        for i in range(num_matches):
            match = self.simulate_match()
            print(f"  Match {i+1}: {match.player1} vs {match.player2} -> Winner: {match.winner}")

        print(f"\nSimulation complete! Total players: {len(self.players)}")
        self.save_leaderboard()

    def save_leaderboard(self):
        """Save leaderboard to file."""
        leaderboard = self.get_leaderboard(100)
        filepath = SAVE_DIR / "leaderboard.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                "updated_at": datetime.now().isoformat(),
                "total_players": len(self.players),
                "rankings": leaderboard
            }, f, indent=2, ensure_ascii=False)
        print(f"Leaderboard saved to {filepath}")

    def display_leaderboard(self, top_n: int = 20):
        """Display leaderboard in console."""
        print("\n" + "="*70)
        print("  KOF ULTIMATE ONLINE - LEADERBOARD")
        print("="*70)
        print(f"{'Rank':<6}{'Player':<20}{'ELO':<8}{'Title':<15}{'W/L':<10}{'WR%':<8}")
        print("-"*70)

        for entry in self.get_leaderboard(top_n):
            wl = f"{entry['wins']}/{entry['losses']}"
            print(f"{entry['rank']:<6}{entry['username']:<20}{entry['elo']:<8}{entry['title']:<15}{wl:<10}{entry['winrate']:.1f}%")

        print("="*70)

    def get_player_profile_display(self, username: str) -> str:
        """Get formatted player profile for display."""
        if username not in self.players:
            return f"Player '{username}' not found."

        p = self.players[username]
        rank = self.get_player_rank(username)

        output = f"""
================================================================================
  PLAYER PROFILE: {p.username}
================================================================================
  Rank: #{rank} | Title: {p.title} | ELO: {p.elo}
  Country: {p.country}

  STATS:
  - Wins: {p.wins} | Losses: {p.losses} | Winrate: {p.get_winrate():.1f}%
  - Current Streak: {p.win_streak} | Best Streak: {p.max_win_streak}
  - Total Matches: {p.total_matches}
  - Rounds Won: {p.total_rounds_won} | Rounds Lost: {p.total_rounds_lost}

  MAIN CHARACTERS: {', '.join(p.main_characters) if p.main_characters else 'None'}

  RECENT MATCHES:
"""
        for match in reversed(p.match_history[-10:]):
            elo_str = f"+{match['elo_change']}" if match['elo_change'] > 0 else str(match['elo_change'])
            output += f"    {match['result']:<5} vs {match['opponent']:<15} ({elo_str} ELO) - {match['my_char']} vs {match['opp_char']}\n"

        output += "================================================================================"
        return output


def main():
    """Main function for testing."""
    print("KOF Ultimate Online System")
    print("="*50)

    system = OnlineSystem()

    # Simulate some matches if no players exist
    if len(system.players) < 10:
        print("Initializing with simulated matches...")
        system.simulate_tournament(100)

    # Display leaderboard
    system.display_leaderboard(20)

    # Show a random player profile
    if system.players:
        random_player = random.choice(list(system.players.keys()))
        print(system.get_player_profile_display(random_player))


if __name__ == "__main__":
    main()
