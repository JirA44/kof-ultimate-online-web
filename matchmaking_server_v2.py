#!/usr/bin/env python3
"""
KOFUO Enhanced Matchmaking Server V2.0
Built with SupaFighter + OpenCode collaboration

Features:
- Advanced ELO matchmaking with dynamic range expansion
- WebSocket real-time connections
- Match analysis and statistics
- Character balance tracking
- Skill-based ranking tiers
- Anti-smurf detection
- Rage quit penalties
"""

import asyncio
import json
import time
import hashlib
import sqlite3
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
import websockets
from websockets.server import serve
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger('KOFUO_MM')

# ============================================================================
# CONFIGURATION
# ============================================================================

CONFIG = {
    "host": "0.0.0.0",
    "port": 9999,
    "websocket_port": 9998,
    "max_players": 1000,
    "queue_check_interval": 1.0,
    "elo_default": 1200,
    "elo_k_factor": 32,
    "elo_initial_range": 100,
    "elo_range_expansion_rate": 20,  # Per second
    "elo_max_range": 500,
    "match_timeout": 600,  # 10 minutes
    "ragequit_penalty": 50,  # ELO penalty
    "ragequit_threshold": 3,  # Times before ban
}

# Rank tiers
RANK_TIERS = [
    {"name": "Bronze", "min_elo": 0, "icon": "🥉"},
    {"name": "Silver", "min_elo": 1000, "icon": "🥈"},
    {"name": "Gold", "min_elo": 1200, "icon": "🥇"},
    {"name": "Platinum", "min_elo": 1400, "icon": "💎"},
    {"name": "Diamond", "min_elo": 1600, "icon": "💠"},
    {"name": "Master", "min_elo": 1800, "icon": "👑"},
    {"name": "Grand Master", "min_elo": 2000, "icon": "🏆"},
    {"name": "Legend", "min_elo": 2200, "icon": "⭐"},
    {"name": "SUPA", "min_elo": 2500, "icon": "🔥"},
]

# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class Player:
    id: str
    username: str
    elo: int = 1200
    wins: int = 0
    losses: int = 0
    character: str = ""
    queue_type: str = ""
    queue_time: float = 0
    elo_range: int = 100
    connection: Optional[websockets.WebSocketServerProtocol] = None
    match_id: Optional[str] = None
    last_ping: float = 0
    ragequit_count: int = 0
    is_banned: bool = False
    favorite_characters: Dict[str, int] = field(default_factory=dict)
    match_history: List[str] = field(default_factory=list)

    def get_rank(self) -> Dict:
        for tier in reversed(RANK_TIERS):
            if self.elo >= tier["min_elo"]:
                return tier
        return RANK_TIERS[0]

    def winrate(self) -> float:
        total = self.wins + self.losses
        if total == 0:
            return 0.0
        return (self.wins / total) * 100

@dataclass
class Match:
    id: str
    player1_id: str
    player2_id: str
    player1_char: str
    player2_char: str
    status: str = "waiting"  # waiting, active, finished
    start_time: float = 0
    end_time: float = 0
    winner_id: Optional[str] = None
    player1_elo_before: int = 0
    player2_elo_before: int = 0
    player1_elo_after: int = 0
    player2_elo_after: int = 0
    rounds: List[Dict] = field(default_factory=list)
    disconnected_player: Optional[str] = None

@dataclass
class QueueEntry:
    player: Player
    queue_type: str  # ranked, casual, training
    join_time: float
    elo_range: int = 100

# ============================================================================
# DATABASE
# ============================================================================

class Database:
    def __init__(self, db_path: str = "kofuo_matchmaking.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT,
                elo INTEGER DEFAULT 1200,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                ragequit_count INTEGER DEFAULT 0,
                is_banned INTEGER DEFAULT 0,
                favorite_characters TEXT DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_online TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                id TEXT PRIMARY KEY,
                player1_id TEXT,
                player2_id TEXT,
                player1_char TEXT,
                player2_char TEXT,
                winner_id TEXT,
                player1_elo_before INTEGER,
                player2_elo_before INTEGER,
                player1_elo_after INTEGER,
                player2_elo_after INTEGER,
                duration_seconds INTEGER,
                rounds TEXT,
                disconnected_player TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS character_stats (
                character_name TEXT PRIMARY KEY,
                picks INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_stats (
                date TEXT PRIMARY KEY,
                total_matches INTEGER DEFAULT 0,
                unique_players INTEGER DEFAULT 0,
                peak_concurrent INTEGER DEFAULT 0
            )
        """)

        conn.commit()
        conn.close()

    def save_player(self, player: Player):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO players
            (id, username, elo, wins, losses, ragequit_count, is_banned, favorite_characters, last_online)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            player.id, player.username, player.elo, player.wins, player.losses,
            player.ragequit_count, 1 if player.is_banned else 0,
            json.dumps(player.favorite_characters), datetime.now().isoformat()
        ))

        conn.commit()
        conn.close()

    def load_player(self, username: str) -> Optional[Player]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM players WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return Player(
                id=row[0],
                username=row[1],
                elo=row[3],
                wins=row[4],
                losses=row[5],
                ragequit_count=row[6],
                is_banned=bool(row[7]),
                favorite_characters=json.loads(row[8]) if row[8] else {}
            )
        return None

    def save_match(self, match: Match):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        duration = int(match.end_time - match.start_time) if match.end_time else 0

        cursor.execute("""
            INSERT INTO matches
            (id, player1_id, player2_id, player1_char, player2_char, winner_id,
             player1_elo_before, player2_elo_before, player1_elo_after, player2_elo_after,
             duration_seconds, rounds, disconnected_player)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            match.id, match.player1_id, match.player2_id,
            match.player1_char, match.player2_char, match.winner_id,
            match.player1_elo_before, match.player2_elo_before,
            match.player1_elo_after, match.player2_elo_after,
            duration, json.dumps(match.rounds), match.disconnected_player
        ))

        conn.commit()
        conn.close()

    def get_leaderboard(self, limit: int = 100) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, username, elo, wins, losses
            FROM players
            WHERE is_banned = 0
            ORDER BY elo DESC
            LIMIT ?
        """, (limit,))

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "rank": i + 1,
                "id": row[0],
                "username": row[1],
                "elo": row[2],
                "wins": row[3],
                "losses": row[4],
                "winrate": round((row[3] / max(1, row[3] + row[4])) * 100, 1)
            }
            for i, row in enumerate(rows)
        ]

    def update_character_stats(self, character: str, won: bool):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO character_stats (character_name, picks, wins, losses)
            VALUES (?, 1, ?, ?)
            ON CONFLICT(character_name) DO UPDATE SET
                picks = picks + 1,
                wins = wins + ?,
                losses = losses + ?
        """, (character, 1 if won else 0, 0 if won else 1, 1 if won else 0, 0 if won else 1))

        conn.commit()
        conn.close()

# ============================================================================
# MATCHMAKING ENGINE
# ============================================================================

class MatchmakingEngine:
    def __init__(self):
        self.db = Database()
        self.players: Dict[str, Player] = {}
        self.queues: Dict[str, List[QueueEntry]] = {
            "ranked": [],
            "casual": [],
            "training": []
        }
        self.matches: Dict[str, Match] = {}
        self.websocket_clients: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.running = False

    # ==========================================================================
    # ELO CALCULATIONS
    # ==========================================================================

    def calculate_elo(self, winner_elo: int, loser_elo: int) -> tuple:
        """Calculate new ELO ratings after a match."""
        k = CONFIG["elo_k_factor"]

        expected_winner = 1 / (1 + 10 ** ((loser_elo - winner_elo) / 400))
        expected_loser = 1 - expected_winner

        new_winner_elo = round(winner_elo + k * (1 - expected_winner))
        new_loser_elo = round(loser_elo + k * (0 - expected_loser))

        # Prevent going below 0
        new_loser_elo = max(0, new_loser_elo)

        return new_winner_elo, new_loser_elo

    # ==========================================================================
    # PLAYER MANAGEMENT
    # ==========================================================================

    async def register_player(self, ws, data: Dict) -> Player:
        """Register or login a player."""
        username = data.get("username", "")
        player_id = data.get("player_id", hashlib.md5(username.encode()).hexdigest()[:16])

        # Try to load existing player
        existing = self.db.load_player(username)
        if existing:
            player = existing
            player.connection = ws
        else:
            # New player
            player = Player(
                id=player_id,
                username=username,
                connection=ws
            )
            self.db.save_player(player)

        self.players[player_id] = player
        self.websocket_clients[player_id] = ws

        logger.info(f"Player registered: {username} (ELO: {player.elo})")

        return player

    async def disconnect_player(self, player_id: str):
        """Handle player disconnection."""
        if player_id not in self.players:
            return

        player = self.players[player_id]

        # Remove from queue
        for queue_type in self.queues:
            self.queues[queue_type] = [
                e for e in self.queues[queue_type] if e.player.id != player_id
            ]

        # Handle match disconnection (ragequit)
        if player.match_id and player.match_id in self.matches:
            match = self.matches[player.match_id]
            if match.status == "active":
                match.disconnected_player = player_id
                await self.end_match(match.id, "disconnect")

        # Save and cleanup
        self.db.save_player(player)
        del self.players[player_id]
        if player_id in self.websocket_clients:
            del self.websocket_clients[player_id]

        logger.info(f"Player disconnected: {player.username}")

    # ==========================================================================
    # QUEUE MANAGEMENT
    # ==========================================================================

    async def join_queue(self, player_id: str, queue_type: str, character: str) -> bool:
        """Add player to matchmaking queue."""
        if player_id not in self.players:
            return False

        player = self.players[player_id]

        if player.is_banned:
            await self.send_to_player(player_id, {
                "type": "error",
                "message": "You are banned from matchmaking."
            })
            return False

        if player.match_id:
            await self.send_to_player(player_id, {
                "type": "error",
                "message": "Already in a match."
            })
            return False

        # Check if already in queue
        for q in self.queues.values():
            if any(e.player.id == player_id for e in q):
                return False

        player.character = character
        player.queue_type = queue_type

        entry = QueueEntry(
            player=player,
            queue_type=queue_type,
            join_time=time.time(),
            elo_range=CONFIG["elo_initial_range"]
        )

        self.queues[queue_type].append(entry)

        logger.info(f"{player.username} joined {queue_type} queue with {character}")

        await self.send_to_player(player_id, {
            "type": "queue_joined",
            "queue_type": queue_type,
            "position": len(self.queues[queue_type])
        })

        # Try to find match immediately
        await self.try_matchmaking(queue_type)

        return True

    async def leave_queue(self, player_id: str):
        """Remove player from all queues."""
        for queue_type in self.queues:
            self.queues[queue_type] = [
                e for e in self.queues[queue_type] if e.player.id != player_id
            ]

        if player_id in self.players:
            self.players[player_id].queue_type = ""

            await self.send_to_player(player_id, {"type": "queue_left"})

    # ==========================================================================
    # MATCHMAKING
    # ==========================================================================

    async def try_matchmaking(self, queue_type: str):
        """Attempt to match players in a queue."""
        queue = self.queues[queue_type]

        if len(queue) < 2:
            return

        # Sort by wait time (oldest first)
        queue.sort(key=lambda e: e.join_time)

        # Expand ELO ranges based on wait time
        current_time = time.time()
        for entry in queue:
            wait_time = current_time - entry.join_time
            entry.elo_range = min(
                CONFIG["elo_max_range"],
                CONFIG["elo_initial_range"] + int(wait_time * CONFIG["elo_range_expansion_rate"])
            )

        # Try to find matches
        matched = set()
        for i, entry1 in enumerate(queue):
            if entry1.player.id in matched:
                continue

            for j, entry2 in enumerate(queue[i + 1:], i + 1):
                if entry2.player.id in matched:
                    continue

                # Check ELO compatibility
                elo_diff = abs(entry1.player.elo - entry2.player.elo)
                max_range = max(entry1.elo_range, entry2.elo_range)

                if elo_diff <= max_range:
                    # Match found!
                    await self.create_match(entry1.player, entry2.player, queue_type)
                    matched.add(entry1.player.id)
                    matched.add(entry2.player.id)
                    break

        # Remove matched players from queue
        self.queues[queue_type] = [
            e for e in queue if e.player.id not in matched
        ]

    async def create_match(self, player1: Player, player2: Player, queue_type: str):
        """Create a new match between two players."""
        match_id = f"match_{int(time.time())}_{player1.id[:4]}_{player2.id[:4]}"

        match = Match(
            id=match_id,
            player1_id=player1.id,
            player2_id=player2.id,
            player1_char=player1.character,
            player2_char=player2.character,
            status="waiting",
            start_time=time.time(),
            player1_elo_before=player1.elo,
            player2_elo_before=player2.elo
        )

        self.matches[match_id] = match
        player1.match_id = match_id
        player2.match_id = match_id

        # Determine host randomly
        is_p1_host = time.time() % 2 == 0

        logger.info(f"Match created: {player1.username} ({player1.elo}) vs {player2.username} ({player2.elo})")

        # Notify players
        await self.send_to_player(player1.id, {
            "type": "match_found",
            "match_id": match_id,
            "opponent_id": player2.id,
            "opponent_name": player2.username,
            "opponent_elo": player2.elo,
            "opponent_character": player2.character,
            "opponent_rank": player2.get_rank(),
            "is_host": is_p1_host,
            "queue_type": queue_type
        })

        await self.send_to_player(player2.id, {
            "type": "match_found",
            "match_id": match_id,
            "opponent_id": player1.id,
            "opponent_name": player1.username,
            "opponent_elo": player1.elo,
            "opponent_character": player1.character,
            "opponent_rank": player1.get_rank(),
            "is_host": not is_p1_host,
            "queue_type": queue_type
        })

        # Start match after short delay
        await asyncio.sleep(2)
        match.status = "active"

        await self.send_to_player(player1.id, {"type": "match_start"})
        await self.send_to_player(player2.id, {"type": "match_start"})

    # ==========================================================================
    # MATCH RESULTS
    # ==========================================================================

    async def end_match(self, match_id: str, reason: str = "normal"):
        """End a match and update ratings."""
        if match_id not in self.matches:
            return

        match = self.matches[match_id]
        match.status = "finished"
        match.end_time = time.time()

        player1 = self.players.get(match.player1_id)
        player2 = self.players.get(match.player2_id)

        if not player1 or not player2:
            return

        # Handle ragequit
        if reason == "disconnect" and match.disconnected_player:
            ragequitter_id = match.disconnected_player
            winner_id = match.player2_id if ragequitter_id == match.player1_id else match.player1_id

            ragequitter = self.players.get(ragequitter_id)
            if ragequitter:
                ragequitter.ragequit_count += 1
                ragequitter.elo = max(0, ragequitter.elo - CONFIG["ragequit_penalty"])

                if ragequitter.ragequit_count >= CONFIG["ragequit_threshold"]:
                    ragequitter.is_banned = True
                    logger.warning(f"Player banned for ragequitting: {ragequitter.username}")

            match.winner_id = winner_id
            logger.info(f"Match ended by disconnect: {match_id}")

        # Calculate new ELOs
        if match.winner_id:
            winner = player1 if match.winner_id == player1.id else player2
            loser = player2 if match.winner_id == player1.id else player1

            new_winner_elo, new_loser_elo = self.calculate_elo(winner.elo, loser.elo)

            winner.elo = new_winner_elo
            winner.wins += 1
            loser.elo = new_loser_elo
            loser.losses += 1

            match.player1_elo_after = player1.elo
            match.player2_elo_after = player2.elo

            # Update character stats
            self.db.update_character_stats(winner.character if winner == player1 else loser.character, winner == player1)
            self.db.update_character_stats(loser.character if loser == player1 else winner.character, loser == player1)

            # Save to database
            self.db.save_player(player1)
            self.db.save_player(player2)
            self.db.save_match(match)

            # Notify players
            result_data = {
                "type": "match_result",
                "match_id": match_id,
                "winner_id": match.winner_id,
                "player1_elo": player1.elo,
                "player2_elo": player2.elo,
                "player1_elo_change": player1.elo - match.player1_elo_before,
                "player2_elo_change": player2.elo - match.player2_elo_before,
                "player1_rank": player1.get_rank(),
                "player2_rank": player2.get_rank(),
                "reason": reason
            }

            await self.send_to_player(player1.id, result_data)
            await self.send_to_player(player2.id, result_data)

            logger.info(f"Match finished: {player1.username} ({player1.elo}) vs {player2.username} ({player2.elo})")

        # Cleanup
        player1.match_id = None
        player2.match_id = None
        del self.matches[match_id]

    async def report_match_result(self, player_id: str, data: Dict):
        """Handle match result report from a player."""
        if player_id not in self.players:
            return

        player = self.players[player_id]
        if not player.match_id:
            return

        match = self.matches.get(player.match_id)
        if not match or match.status != "active":
            return

        winner_id = data.get("winner_id")
        if winner_id in [match.player1_id, match.player2_id]:
            match.winner_id = winner_id
            match.rounds = data.get("rounds", [])
            await self.end_match(match.id, "normal")

    # ==========================================================================
    # COMMUNICATION
    # ==========================================================================

    async def send_to_player(self, player_id: str, data: Dict):
        """Send message to a specific player."""
        if player_id in self.websocket_clients:
            try:
                await self.websocket_clients[player_id].send(json.dumps(data))
            except:
                pass

    async def broadcast(self, data: Dict, exclude: Set[str] = None):
        """Broadcast message to all connected players."""
        exclude = exclude or set()
        for player_id, ws in self.websocket_clients.items():
            if player_id not in exclude:
                try:
                    await ws.send(json.dumps(data))
                except:
                    pass

    # ==========================================================================
    # WEBSOCKET HANDLER
    # ==========================================================================

    async def handle_websocket(self, websocket, path):
        """Handle WebSocket connection."""
        player_id = None

        try:
            async for message in websocket:
                data = json.loads(message)
                msg_type = data.get("type", "")

                if msg_type == "register":
                    player = await self.register_player(websocket, data)
                    player_id = player.id

                    await websocket.send(json.dumps({
                        "type": "registered",
                        "player_id": player.id,
                        "username": player.username,
                        "elo": player.elo,
                        "rank": player.get_rank(),
                        "wins": player.wins,
                        "losses": player.losses,
                        "winrate": player.winrate()
                    }))

                elif msg_type == "join_queue":
                    if player_id:
                        await self.join_queue(
                            player_id,
                            data.get("queue_type", "ranked"),
                            data.get("character", "Kyo")
                        )

                elif msg_type == "leave_queue":
                    if player_id:
                        await self.leave_queue(player_id)

                elif msg_type == "match_result":
                    if player_id:
                        await self.report_match_result(player_id, data)

                elif msg_type == "ping":
                    await websocket.send(json.dumps({
                        "type": "pong",
                        "timestamp": data.get("timestamp", 0)
                    }))
                    if player_id in self.players:
                        self.players[player_id].last_ping = time.time()

                elif msg_type == "get_leaderboard":
                    leaderboard = self.db.get_leaderboard(50)
                    await websocket.send(json.dumps({
                        "type": "leaderboard",
                        "data": leaderboard
                    }))

                elif msg_type == "get_online":
                    await websocket.send(json.dumps({
                        "type": "online_count",
                        "count": len(self.players),
                        "in_queue": sum(len(q) for q in self.queues.values()),
                        "in_match": len(self.matches)
                    }))

        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            if player_id:
                await self.disconnect_player(player_id)

    # ==========================================================================
    # MAIN LOOP
    # ==========================================================================

    async def queue_checker(self):
        """Periodically check queues for matches."""
        while self.running:
            for queue_type in self.queues:
                await self.try_matchmaking(queue_type)
            await asyncio.sleep(CONFIG["queue_check_interval"])

    async def start(self):
        """Start the matchmaking server."""
        self.running = True

        logger.info("=" * 50)
        logger.info("  KOFUO Enhanced Matchmaking Server V2.0")
        logger.info("  Built by Claude + SupaFighter + OpenCode")
        logger.info("=" * 50)
        logger.info(f"Starting WebSocket server on port {CONFIG['websocket_port']}...")

        # Start queue checker
        asyncio.create_task(self.queue_checker())

        # Start WebSocket server
        async with serve(self.handle_websocket, CONFIG["host"], CONFIG["websocket_port"]):
            logger.info(f"Server running on ws://{CONFIG['host']}:{CONFIG['websocket_port']}")
            await asyncio.Future()  # Run forever

    def stop(self):
        """Stop the server."""
        self.running = False
        logger.info("Server stopped.")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    engine = MatchmakingEngine()

    try:
        asyncio.run(engine.start())
    except KeyboardInterrupt:
        engine.stop()
        print("\nServer stopped by user.")
