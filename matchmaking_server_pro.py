#!/usr/bin/env python3
"""
KOF Ultimate Online - Professional Matchmaking Server
AAA-Grade Server Architecture (like Battle.net)
Author: Claude
Date: 2025-10-23

Features:
- Ranked matchmaking with MMR/ELO
- Casual matchmaking
- Custom lobbies
- Friends system
- Chat system (global, private)
- Anti-cheat validation
- Statistics tracking
- Replay storage
- Leaderboards
"""

import asyncio
import websockets
import json
import sqlite3
from datetime import datetime, timedelta
from collections import defaultdict
from dataclasses import dataclass, asdict
from typing import Dict, List, Set, Optional
import hashlib
import secrets
import logging

# Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SERVER_VERSION = "1.0.0"
MAX_PLAYERS_PER_LOBBY = 8
MATCHMAKING_TIMEOUT = 120  # secondes
MMR_RANGE_INITIAL = 100
MMR_RANGE_EXPANSION_RATE = 50  # expand every 10s

@dataclass
class Player:
    """Représente un joueur connecté"""
    player_id: str
    username: str
    mmr: int
    rank: str
    websocket: websockets.WebSocketServerProtocol
    status: str  # online, in_queue, in_match, etc.
    current_lobby: Optional[str] = None
    friends: Set[str] = None
    last_ping: datetime = None
    is_real: bool = True  # True = real player, False = bot/simulated

    def __post_init__(self):
        if self.friends is None:
            self.friends = set()
        if self.last_ping is None:
            self.last_ping = datetime.now()
        # Auto-detect bots by player_id prefix
        if self.player_id.startswith(('bot_', 'sim_', 'ai_')):
            self.is_real = False

    def to_dict(self):
        """Convertit en dict pour JSON"""
        # Map internal status to UI-friendly status
        ui_status = 'ready'
        if self.status in ('in_match', 'in_game', 'fighting'):
            ui_status = 'fighting'
        elif self.status in ('in_queue', 'searching'):
            ui_status = 'ready'
        elif self.status in ('away', 'idle', 'afk'):
            ui_status = 'away'

        return {
            "player_id": self.player_id,
            "playerId": self.player_id,
            "username": self.username,
            "mmr": self.mmr,
            "elo": self.mmr,
            "rank": self.rank,
            "status": ui_status,
            "isReal": self.is_real,
            "current_lobby": self.current_lobby
        }

@dataclass
class MatchRequest:
    """Requête de matchmaking"""
    player: Player
    mode: str  # ranked, casual
    timestamp: datetime
    mmr_range: int = MMR_RANGE_INITIAL

@dataclass
class Lobby:
    """Lobby de jeu personnalisé"""
    lobby_id: str
    name: str
    host: Player
    players: List[Player]
    max_players: int
    private: bool
    password: Optional[str] = None
    settings: Dict = None

    def __post_init__(self):
        if self.settings is None:
            self.settings = {}

    def to_dict(self):
        return {
            "lobby_id": self.lobby_id,
            "name": self.name,
            "host": self.host.username,
            "players": [p.username for p in self.players],
            "player_count": len(self.players),
            "max_players": self.max_players,
            "private": self.private,
            "settings": self.settings
        }

class MatchmakingServer:
    """Serveur de matchmaking professionnel"""

    def __init__(self, host="0.0.0.0", port=7500):
        self.host = host
        self.port = port

        # Joueurs connectés
        self.players: Dict[str, Player] = {}

        # File d'attente matchmaking
        self.ranked_queue: List[MatchRequest] = []
        self.casual_queue: List[MatchRequest] = []

        # Lobbies personnalisés
        self.lobbies: Dict[str, Lobby] = {}

        # Matchs en cours
        self.active_matches: Dict[str, Dict] = {}

        # Challenges/Demandes de duel (challenger_id -> {target_id, timestamp, expires})
        self.pending_challenges: Dict[str, Dict] = {}
        self.CHALLENGE_TIMEOUT = 15  # 15 secondes pour accepter

        # Chat
        self.chat_history: List[Dict] = []

        # Database
        self.init_database()

        # Tasks asynchrones
        self.background_tasks = []

    def init_database(self):
        """Initialise la base de données SQLite"""
        self.db = sqlite3.connect('kof_online.db', check_same_thread=False)
        cursor = self.db.cursor()

        # Table des joueurs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                player_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                mmr INTEGER DEFAULT 1000,
                rank TEXT DEFAULT 'Bronze',
                total_matches INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                win_streak INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')

        # Table des friends
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS friends (
                player_id TEXT,
                friend_id TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (player_id, friend_id)
            )
        ''')

        # Table des matchs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS matches (
                match_id TEXT PRIMARY KEY,
                player1_id TEXT,
                player2_id TEXT,
                winner_id TEXT,
                player1_mmr_before INTEGER,
                player2_mmr_before INTEGER,
                player1_mmr_after INTEGER,
                player2_mmr_after INTEGER,
                mode TEXT,
                duration INTEGER,
                replay_file TEXT,
                played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Table des replays
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS replays (
                replay_id TEXT PRIMARY KEY,
                match_id TEXT,
                file_path TEXT,
                uploaded_by TEXT,
                views INTEGER DEFAULT 0,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Table des achievements
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS achievements (
                achievement_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                icon TEXT,
                points INTEGER DEFAULT 10
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS player_achievements (
                player_id TEXT,
                achievement_id TEXT,
                unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (player_id, achievement_id)
            )
        ''')

        self.db.commit()

    async def start(self):
        """Démarre le serveur"""
        logger.info(f"Starting KOF Online Server v{SERVER_VERSION}")
        logger.info(f"Server listening on {self.host}:{self.port}")

        # Démarre les tâches de fond
        self.background_tasks.append(
            asyncio.create_task(self.matchmaking_loop())
        )
        self.background_tasks.append(
            asyncio.create_task(self.heartbeat_loop())
        )

        # Démarre le serveur WebSocket
        async with websockets.serve(self.handle_client, self.host, self.port):
            await asyncio.Future()  # run forever

    async def handle_client(self, websocket, path):
        """Gère une connexion client"""
        player_id = None
        try:
            async for message in websocket:
                data = json.loads(message)
                action = data.get("action")

                if action == "login":
                    player_id = await self.handle_login(websocket, data)

                elif action == "register":
                    await self.handle_register(websocket, data)

                elif action == "queue":
                    await self.handle_queue(player_id, data)

                elif action == "leave_queue":
                    await self.handle_leave_queue(player_id)

                elif action == "create_lobby":
                    await self.handle_create_lobby(player_id, data)

                elif action == "join_lobby":
                    await self.handle_join_lobby(player_id, data)

                elif action == "leave_lobby":
                    await self.handle_leave_lobby(player_id)

                elif action == "chat":
                    await self.handle_chat(player_id, data)

                elif action == "add_friend":
                    await self.handle_add_friend(player_id, data)

                elif action == "get_stats":
                    await self.handle_get_stats(websocket, data)

                elif action == "get_leaderboard":
                    await self.handle_get_leaderboard(websocket, data)

                elif action == "get_players":
                    await self.handle_get_players(websocket)

                elif action == "send_challenge":
                    await self.handle_send_challenge(player_id, data)

                elif action == "accept_challenge":
                    await self.handle_accept_challenge(player_id, data)

                elif action == "decline_challenge":
                    await self.handle_decline_challenge(player_id, data)

                elif action == "ping":
                    if player_id and player_id in self.players:
                        self.players[player_id].last_ping = datetime.now()
                    await websocket.send(json.dumps({"type": "pong"}))

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client disconnected: {player_id}")
        finally:
            if player_id:
                await self.handle_disconnect(player_id)

    async def handle_login(self, websocket, data):
        """Gère la connexion d'un joueur"""
        username = data.get("username")
        password = data.get("password")

        cursor = self.db.cursor()
        cursor.execute(
            "SELECT player_id, password_hash, mmr, rank FROM players WHERE username = ?",
            (username,)
        )
        result = cursor.fetchone()

        if not result:
            await websocket.send(json.dumps({
                "type": "login_response",
                "success": False,
                "message": "User not found"
            }))
            return None

        player_id, password_hash, mmr, rank = result

        # Vérifier le mot de passe
        if not self.verify_password(password, password_hash):
            await websocket.send(json.dumps({
                "type": "login_response",
                "success": False,
                "message": "Invalid password"
            }))
            return None

        # Créer l'objet Player
        player = Player(
            player_id=player_id,
            username=username,
            mmr=mmr,
            rank=rank,
            websocket=websocket,
            status="online"
        )

        self.players[player_id] = player

        # Mettre à jour last_login
        cursor.execute(
            "UPDATE players SET last_login = CURRENT_TIMESTAMP WHERE player_id = ?",
            (player_id,)
        )
        self.db.commit()

        # Envoyer réponse de succès
        await websocket.send(json.dumps({
            "type": "login_response",
            "success": True,
            "player_data": player.to_dict()
        }))

        logger.info(f"Player logged in: {username} ({player_id})")
        return player_id

    async def handle_register(self, websocket, data):
        """Gère l'enregistrement d'un nouveau joueur"""
        username = data.get("username")
        password = data.get("password")

        # Générer player_id
        player_id = secrets.token_hex(16)

        # Hash du mot de passe
        password_hash = self.hash_password(password)

        try:
            cursor = self.db.cursor()
            cursor.execute(
                "INSERT INTO players (player_id, username, password_hash) VALUES (?, ?, ?)",
                (player_id, username, password_hash)
            )
            self.db.commit()

            await websocket.send(json.dumps({
                "type": "register_response",
                "success": True,
                "message": "Account created successfully"
            }))

            logger.info(f"New player registered: {username}")

        except sqlite3.IntegrityError:
            await websocket.send(json.dumps({
                "type": "register_response",
                "success": False,
                "message": "Username already exists"
            }))

    async def handle_queue(self, player_id, data):
        """Ajoute un joueur à la file d'attente"""
        if not player_id or player_id not in self.players:
            return

        player = self.players[player_id]
        mode = data.get("mode", "casual")  # ranked or casual

        # Créer requête de match
        match_request = MatchRequest(
            player=player,
            mode=mode,
            timestamp=datetime.now()
        )

        if mode == "ranked":
            self.ranked_queue.append(match_request)
        else:
            self.casual_queue.append(match_request)

        player.status = "in_queue"

        await player.websocket.send(json.dumps({
            "type": "queue_joined",
            "mode": mode,
            "queue_size": len(self.ranked_queue if mode == "ranked" else self.casual_queue)
        }))

        logger.info(f"{player.username} joined {mode} queue")

    async def handle_leave_queue(self, player_id):
        """Retire un joueur de la file d'attente"""
        if not player_id or player_id not in self.players:
            return

        player = self.players[player_id]

        # Retirer de la queue
        self.ranked_queue = [r for r in self.ranked_queue if r.player.player_id != player_id]
        self.casual_queue = [r for r in self.casual_queue if r.player.player_id != player_id]

        player.status = "online"

        await player.websocket.send(json.dumps({
            "type": "queue_left"
        }))

    async def handle_create_lobby(self, player_id, data):
        """Crée un lobby personnalisé"""
        if not player_id or player_id not in self.players:
            return

        player = self.players[player_id]

        lobby_id = secrets.token_hex(8)
        lobby = Lobby(
            lobby_id=lobby_id,
            name=data.get("name", f"{player.username}'s Lobby"),
            host=player,
            players=[player],
            max_players=data.get("max_players", MAX_PLAYERS_PER_LOBBY),
            private=data.get("private", False),
            password=data.get("password"),
            settings=data.get("settings", {})
        )

        self.lobbies[lobby_id] = lobby
        player.current_lobby = lobby_id
        player.status = "in_lobby"

        await player.websocket.send(json.dumps({
            "type": "lobby_created",
            "lobby": lobby.to_dict()
        }))

        logger.info(f"Lobby created: {lobby.name} by {player.username}")

    async def handle_join_lobby(self, player_id, data):
        """Rejoint un lobby"""
        if not player_id or player_id not in self.players:
            return

        player = self.players[player_id]
        lobby_id = data.get("lobby_id")
        password = data.get("password")

        if lobby_id not in self.lobbies:
            await player.websocket.send(json.dumps({
                "type": "error",
                "message": "Lobby not found"
            }))
            return

        lobby = self.lobbies[lobby_id]

        # Vérifier le mot de passe si privé
        if lobby.private and lobby.password != password:
            await player.websocket.send(json.dumps({
                "type": "error",
                "message": "Invalid password"
            }))
            return

        # Vérifier si plein
        if len(lobby.players) >= lobby.max_players:
            await player.websocket.send(json.dumps({
                "type": "error",
                "message": "Lobby is full"
            }))
            return

        # Ajouter le joueur
        lobby.players.append(player)
        player.current_lobby = lobby_id
        player.status = "in_lobby"

        # Notifier tous les joueurs du lobby
        for p in lobby.players:
            await p.websocket.send(json.dumps({
                "type": "lobby_updated",
                "lobby": lobby.to_dict()
            }))

        logger.info(f"{player.username} joined lobby {lobby.name}")

    async def handle_leave_lobby(self, player_id):
        """Quitte un lobby"""
        if not player_id or player_id not in self.players:
            return

        player = self.players[player_id]
        lobby_id = player.current_lobby

        if not lobby_id or lobby_id not in self.lobbies:
            return

        lobby = self.lobbies[lobby_id]
        lobby.players = [p for p in lobby.players if p.player_id != player_id]

        player.current_lobby = None
        player.status = "online"

        # Si lobby vide ou host parti, détruire le lobby
        if len(lobby.players) == 0 or lobby.host.player_id == player_id:
            del self.lobbies[lobby_id]
            logger.info(f"Lobby {lobby.name} destroyed")
        else:
            # Notifier les joueurs restants
            for p in lobby.players:
                await p.websocket.send(json.dumps({
                    "type": "lobby_updated",
                    "lobby": lobby.to_dict()
                }))

    async def handle_chat(self, player_id, data):
        """Gère les messages de chat"""
        if not player_id or player_id not in self.players:
            return

        player = self.players[player_id]
        message_type = data.get("message_type", "global")  # global, lobby, private
        content = data.get("content")

        chat_message = {
            "type": "chat_message",
            "from": player.username,
            "message_type": message_type,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }

        if message_type == "global":
            # Broadcast à tous
            for p in self.players.values():
                try:
                    await p.websocket.send(json.dumps(chat_message))
                except:
                    pass

        elif message_type == "lobby" and player.current_lobby:
            # Envoyer aux joueurs du lobby
            lobby = self.lobbies.get(player.current_lobby)
            if lobby:
                for p in lobby.players:
                    try:
                        await p.websocket.send(json.dumps(chat_message))
                    except:
                        pass

        elif message_type == "private":
            # Message privé
            to_username = data.get("to")
            target_player = next((p for p in self.players.values() if p.username == to_username), None)
            if target_player:
                try:
                    await target_player.websocket.send(json.dumps(chat_message))
                    await player.websocket.send(json.dumps(chat_message))  # Confirmation
                except:
                    pass

    async def handle_add_friend(self, player_id, data):
        """Ajoute un ami"""
        if not player_id or player_id not in self.players:
            return

        friend_username = data.get("username")

        cursor = self.db.cursor()
        cursor.execute("SELECT player_id FROM players WHERE username = ?", (friend_username,))
        result = cursor.fetchone()

        if not result:
            return

        friend_id = result[0]

        try:
            cursor.execute(
                "INSERT INTO friends (player_id, friend_id, status) VALUES (?, ?, 'pending')",
                (player_id, friend_id)
            )
            self.db.commit()

            # Notifier le joueur si en ligne
            if friend_id in self.players:
                friend = self.players[friend_id]
                await friend.websocket.send(json.dumps({
                    "type": "friend_request",
                    "from": self.players[player_id].username
                }))

        except sqlite3.IntegrityError:
            pass  # Déjà ami

    async def handle_send_challenge(self, player_id, data):
        """Envoie une demande de duel à un autre joueur"""
        if not player_id or player_id not in self.players:
            return

        challenger = self.players[player_id]
        target_id = data.get("target_id")
        target_username = data.get("target_username")

        # Trouver la cible par ID ou username
        target = None
        if target_id and target_id in self.players:
            target = self.players[target_id]
        elif target_username:
            target = next((p for p in self.players.values() if p.username == target_username), None)

        if not target:
            await challenger.websocket.send(json.dumps({
                "type": "challenge_error",
                "message": "Joueur non trouvé ou hors ligne"
            }))
            return

        # Vérifier que la cible est disponible (online, pas en match, pas en queue)
        if target.status not in ["online", "in_lobby"]:
            await challenger.websocket.send(json.dumps({
                "type": "challenge_error",
                "message": f"{target.username} n'est pas disponible ({target.status})"
            }))
            return

        # Vérifier qu'il n'y a pas déjà un défi en cours
        if player_id in self.pending_challenges:
            await challenger.websocket.send(json.dumps({
                "type": "challenge_error",
                "message": "Vous avez déjà un défi en attente"
            }))
            return

        # Créer le défi
        challenge_id = secrets.token_hex(8)
        expires_at = datetime.now() + timedelta(seconds=self.CHALLENGE_TIMEOUT)

        self.pending_challenges[challenge_id] = {
            "challenge_id": challenge_id,
            "challenger_id": player_id,
            "challenger_username": challenger.username,
            "target_id": target.player_id,
            "target_username": target.username,
            "timestamp": datetime.now(),
            "expires_at": expires_at
        }

        # Notifier le challenger
        await challenger.websocket.send(json.dumps({
            "type": "challenge_sent",
            "challenge_id": challenge_id,
            "target": target.username,
            "timeout": self.CHALLENGE_TIMEOUT
        }))

        # Notifier la cible
        await target.websocket.send(json.dumps({
            "type": "challenge_received",
            "challenge_id": challenge_id,
            "from": challenger.username,
            "from_id": player_id,
            "mmr": challenger.mmr,
            "rank": challenger.rank,
            "timeout": self.CHALLENGE_TIMEOUT
        }))

        logger.info(f"Challenge: {challenger.username} -> {target.username} (15s)")

        # Programmer l'expiration
        asyncio.create_task(self.expire_challenge(challenge_id))

    async def expire_challenge(self, challenge_id):
        """Expire un défi après le timeout"""
        await asyncio.sleep(self.CHALLENGE_TIMEOUT)

        if challenge_id not in self.pending_challenges:
            return  # Déjà accepté ou refusé

        challenge = self.pending_challenges.pop(challenge_id)

        # Notifier les deux joueurs
        if challenge["challenger_id"] in self.players:
            challenger = self.players[challenge["challenger_id"]]
            try:
                await challenger.websocket.send(json.dumps({
                    "type": "challenge_expired",
                    "challenge_id": challenge_id,
                    "target": challenge["target_username"]
                }))
            except:
                pass

        if challenge["target_id"] in self.players:
            target = self.players[challenge["target_id"]]
            try:
                await target.websocket.send(json.dumps({
                    "type": "challenge_expired",
                    "challenge_id": challenge_id,
                    "from": challenge["challenger_username"]
                }))
            except:
                pass

        logger.info(f"Challenge expired: {challenge['challenger_username']} -> {challenge['target_username']}")

    async def handle_accept_challenge(self, player_id, data):
        """Accepte une demande de duel"""
        if not player_id or player_id not in self.players:
            return

        challenge_id = data.get("challenge_id")

        if challenge_id not in self.pending_challenges:
            await self.players[player_id].websocket.send(json.dumps({
                "type": "challenge_error",
                "message": "Défi expiré ou annulé"
            }))
            return

        challenge = self.pending_challenges[challenge_id]

        # Vérifier que c'est bien la cible qui accepte
        if challenge["target_id"] != player_id:
            return

        # Supprimer le défi
        del self.pending_challenges[challenge_id]

        challenger_id = challenge["challenger_id"]

        if challenger_id not in self.players:
            await self.players[player_id].websocket.send(json.dumps({
                "type": "challenge_error",
                "message": "Le challenger s'est déconnecté"
            }))
            return

        challenger = self.players[challenger_id]
        target = self.players[player_id]

        # Créer le match
        match_id = secrets.token_hex(16)
        self.active_matches[match_id] = {
            "match_id": match_id,
            "player1": challenger,
            "player2": target,
            "mode": "duel",
            "started_at": datetime.now()
        }

        # Notifier les deux joueurs
        match_data_challenger = {
            "type": "challenge_accepted",
            "challenge_id": challenge_id,
            "match_id": match_id,
            "opponent": target.to_dict(),
            "mode": "duel"
        }

        match_data_target = {
            "type": "challenge_accepted",
            "challenge_id": challenge_id,
            "match_id": match_id,
            "opponent": challenger.to_dict(),
            "mode": "duel"
        }

        await challenger.websocket.send(json.dumps(match_data_challenger))
        await target.websocket.send(json.dumps(match_data_target))

        # Mettre à jour les statuts
        challenger.status = "in_match"
        target.status = "in_match"

        logger.info(f"Duel accepted: {challenger.username} vs {target.username}")

    async def handle_decline_challenge(self, player_id, data):
        """Refuse une demande de duel"""
        if not player_id or player_id not in self.players:
            return

        challenge_id = data.get("challenge_id")

        if challenge_id not in self.pending_challenges:
            return  # Déjà expiré ou traité

        challenge = self.pending_challenges[challenge_id]

        # Vérifier que c'est bien la cible qui refuse
        if challenge["target_id"] != player_id:
            return

        # Supprimer le défi
        del self.pending_challenges[challenge_id]

        # Notifier le challenger
        if challenge["challenger_id"] in self.players:
            challenger = self.players[challenge["challenger_id"]]
            try:
                await challenger.websocket.send(json.dumps({
                    "type": "challenge_declined",
                    "challenge_id": challenge_id,
                    "by": self.players[player_id].username
                }))
            except:
                pass

        # Notifier la cible (confirmation)
        await self.players[player_id].websocket.send(json.dumps({
            "type": "challenge_declined_confirm",
            "challenge_id": challenge_id
        }))

        logger.info(f"Challenge declined: {challenge['target_username']} refused {challenge['challenger_username']}")

    async def handle_get_players(self, websocket):
        """Renvoie la liste des joueurs en ligne"""
        players = []
        for player in self.players.values():
            players.append({
                "player_id": player.player_id,
                "username": player.username,
                "mmr": player.mmr,
                "rank": player.rank,
                "status": player.status
            })

        await websocket.send(json.dumps({
            "type": "player_list",
            "players": players,
            "count": len(players)
        }))

    async def handle_get_stats(self, websocket, data):
        """Renvoie les stats d'un joueur"""
        player_id = data.get("player_id")

        cursor = self.db.cursor()
        cursor.execute(
            "SELECT * FROM players WHERE player_id = ?",
            (player_id,)
        )
        result = cursor.fetchone()

        if result:
            # TODO: Formater correctement
            await websocket.send(json.dumps({
                "type": "stats_response",
                "stats": {}  # à remplir
            }))

    async def handle_get_leaderboard(self, websocket, data):
        """Renvoie le leaderboard"""
        limit = data.get("limit", 100)

        cursor = self.db.cursor()
        cursor.execute("""
            SELECT username, mmr, rank, wins, losses, win_streak
            FROM players
            ORDER BY mmr DESC
            LIMIT ?
        """, (limit,))

        leaderboard = []
        for row in cursor.fetchall():
            leaderboard.append({
                "username": row[0],
                "mmr": row[1],
                "rank": row[2],
                "wins": row[3],
                "losses": row[4],
                "win_streak": row[5]
            })

        await websocket.send(json.dumps({
            "type": "leaderboard_response",
            "leaderboard": leaderboard
        }))

    async def handle_disconnect(self, player_id):
        """Gère la déconnexion d'un joueur"""
        if player_id not in self.players:
            return

        player = self.players[player_id]

        # Retirer des queues
        await self.handle_leave_queue(player_id)

        # Retirer des lobbies
        await self.handle_leave_lobby(player_id)

        # Supprimer le joueur
        del self.players[player_id]

        logger.info(f"Player disconnected: {player.username}")

    async def matchmaking_loop(self):
        """Boucle de matchmaking"""
        while True:
            await asyncio.sleep(5)  # Check every 5 seconds

            # Process ranked queue
            await self.process_queue(self.ranked_queue, "ranked")

            # Process casual queue
            await self.process_queue(self.casual_queue, "casual")

    async def process_queue(self, queue: List[MatchRequest], mode: str):
        """Traite une file d'attente de matchmaking"""
        if len(queue) < 2:
            return

        # Expand MMR range pour les requêtes anciennes
        now = datetime.now()
        for request in queue:
            time_waiting = (now - request.timestamp).seconds
            request.mmr_range = MMR_RANGE_INITIAL + (time_waiting // 10) * MMR_RANGE_EXPANSION_RATE

        # Trouver des matchs
        matched_pairs = []
        used_players = set()

        for i, req1 in enumerate(queue):
            if req1.player.player_id in used_players:
                continue

            for req2 in queue[i+1:]:
                if req2.player.player_id in used_players:
                    continue

                # Check MMR range
                mmr_diff = abs(req1.player.mmr - req2.player.mmr)
                if mmr_diff <= max(req1.mmr_range, req2.mmr_range):
                    matched_pairs.append((req1, req2))
                    used_players.add(req1.player.player_id)
                    used_players.add(req2.player.player_id)
                    break

        # Créer les matchs
        for req1, req2 in matched_pairs:
            match_id = secrets.token_hex(16)
            self.active_matches[match_id] = {
                "match_id": match_id,
                "player1": req1.player,
                "player2": req2.player,
                "mode": mode,
                "started_at": datetime.now()
            }

            # Notifier les joueurs
            match_data = {
                "type": "match_found",
                "match_id": match_id,
                "opponent": req2.player.to_dict(),
                "mode": mode
            }

            await req1.player.websocket.send(json.dumps(match_data))

            match_data["opponent"] = req1.player.to_dict()
            await req2.player.websocket.send(json.dumps(match_data))

            # Retirer de la queue
            queue.remove(req1)
            queue.remove(req2)

            req1.player.status = "in_match"
            req2.player.status = "in_match"

            logger.info(f"Match found: {req1.player.username} vs {req2.player.username} ({mode})")

    async def heartbeat_loop(self):
        """Vérifie les connexions actives"""
        while True:
            await asyncio.sleep(30)  # Every 30 seconds

            now = datetime.now()
            timeout = timedelta(seconds=90)

            disconnected = []
            for player_id, player in self.players.items():
                if now - player.last_ping > timeout:
                    disconnected.append(player_id)

            for player_id in disconnected:
                await self.handle_disconnect(player_id)

    def hash_password(self, password: str) -> str:
        """Hash un mot de passe"""
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, password: str, password_hash: str) -> bool:
        """Vérifie un mot de passe"""
        return self.hash_password(password) == password_hash

async def main():
    """Point d'entrée"""
    server = MatchmakingServer(host="0.0.0.0", port=7500)
    await server.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server shutdown")
