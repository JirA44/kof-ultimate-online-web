#!/usr/bin/env python3
"""
KOF Ultimate Online - Bridge entre le jeu et le serveur matchmaking
Lit les fichiers JSON du jeu et communique via WebSocket avec le serveur
"""

import asyncio
import websockets
import json
import os
from pathlib import Path
from datetime import datetime

GAME_PATH = Path(__file__).parent
SAVE_PATH = GAME_PATH / "save"
SERVER_URL = "ws://localhost:7500"

class OnlineBridge:
    def __init__(self):
        self.ws = None
        self.player_id = None
        self.username = "LocalPlayer"
        self.running = True

        # S'assurer que le dossier save existe
        SAVE_PATH.mkdir(exist_ok=True)

    def log(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {msg}")

    async def connect(self):
        """Connexion au serveur matchmaking"""
        try:
            self.ws = await websockets.connect(SERVER_URL)
            self.log("Connecte au serveur matchmaking")
            return True
        except Exception as e:
            self.log(f"Erreur connexion: {e}")
            return False

    async def send(self, data):
        """Envoie un message au serveur"""
        if self.ws:
            try:
                await self.ws.send(json.dumps(data))
            except Exception as e:
                self.log(f"Erreur envoi: {e}")

    async def receive_loop(self):
        """Boucle de reception des messages du serveur"""
        try:
            async for message in self.ws:
                data = json.loads(message)
                await self.handle_server_message(data)
        except websockets.exceptions.ConnectionClosed:
            self.log("Connexion fermee")
            self.running = False

    async def handle_server_message(self, data):
        """Traite les messages du serveur"""
        msg_type = data.get("type")

        if msg_type == "pong":
            pass  # Heartbeat

        elif msg_type == "player_list":
            # Liste des joueurs en ligne
            players = data.get("players", [])
            self.write_json("online_players.json", players)
            self.log(f"Liste joueurs mise a jour: {len(players)} joueurs")

        elif msg_type == "challenge_received":
            # Defi recu
            challenge_data = {
                "challenge_id": data.get("challenge_id"),
                "from": data.get("from"),
                "from_id": data.get("from_id"),
                "mmr": data.get("mmr", 1000),
                "rank": data.get("rank", "Bronze"),
                "timeout": data.get("timeout", 15)
            }
            self.write_json("incoming_challenge.json", challenge_data)
            self.log(f"DEFI RECU de {data.get('from')}!")

        elif msg_type == "challenge_sent":
            self.log(f"Defi envoye a {data.get('target')}")

        elif msg_type == "challenge_accepted":
            # Match demarre!
            match_data = {
                "match_id": data.get("match_id"),
                "opponent": data.get("opponent"),
                "mode": data.get("mode", "duel")
            }
            self.write_json("match_start.json", match_data)
            self.log(f"MATCH DEMARRE contre {data.get('opponent', {}).get('username', '?')}")

        elif msg_type == "challenge_declined":
            self.log(f"Defi refuse par {data.get('by')}")
            self.write_json("challenge_result.json", {"status": "declined", "by": data.get("by")})

        elif msg_type == "challenge_expired":
            self.log("Defi expire")
            self.write_json("challenge_result.json", {"status": "expired"})

        elif msg_type == "challenge_error":
            self.log(f"Erreur defi: {data.get('message')}")

        elif msg_type == "match_found":
            # Match trouve via matchmaking
            match_data = {
                "match_id": data.get("match_id"),
                "opponent": data.get("opponent"),
                "mode": data.get("mode")
            }
            self.write_json("match_start.json", match_data)
            self.log(f"MATCH TROUVE! vs {data.get('opponent', {}).get('username', '?')}")

    def write_json(self, filename, data):
        """Ecrit un fichier JSON pour le jeu"""
        path = SAVE_PATH / filename
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def read_json(self, filename):
        """Lit et supprime un fichier JSON du jeu"""
        path = SAVE_PATH / filename
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                os.remove(path)
                return data
            except:
                return None
        return None

    async def check_game_files(self):
        """Verifie les fichiers JSON du jeu"""
        # Challenge request
        data = self.read_json("challenge_request.json")
        if data:
            await self.send({
                "action": "send_challenge",
                "target_id": data.get("to_id"),
                "target_username": data.get("to")
            })
            self.log(f"Envoi defi a {data.get('to')}")

        # Challenge response (accept/decline)
        data = self.read_json("challenge_response.json")
        if data:
            if data.get("type") == "accept_challenge":
                await self.send({
                    "action": "accept_challenge",
                    "challenge_id": data.get("challenge_id")
                })
                self.log("Defi accepte")
            elif data.get("type") == "decline_challenge":
                await self.send({
                    "action": "decline_challenge",
                    "challenge_id": data.get("challenge_id")
                })
                self.log("Defi refuse")

        # Matchmaking request
        data = self.read_json("matchmaking_request.json")
        if data:
            await self.send({
                "action": "queue",
                "mode": data.get("mode", "casual")
            })
            self.log(f"Recherche match {data.get('mode')}")

    async def update_server_status(self):
        """Met a jour le fichier status pour le jeu"""
        # Demander la liste des joueurs
        await self.send({"action": "get_players"})

        # Ecrire le status
        status = {
            "connected": self.ws is not None,
            "players_online": 0,  # Sera mis a jour par le serveur
            "active_matches": 0,
            "queue_ranked": 0,
            "queue_casual": 0,
            "timestamp": datetime.now().isoformat()
        }
        self.write_json("server_status.json", status)

    async def file_check_loop(self):
        """Boucle de verification des fichiers du jeu"""
        while self.running:
            await self.check_game_files()
            await asyncio.sleep(0.5)  # Verification toutes les 500ms

    async def status_update_loop(self):
        """Boucle de mise a jour du status"""
        while self.running:
            await self.update_server_status()
            await asyncio.sleep(2)  # Mise a jour toutes les 2s

    async def heartbeat_loop(self):
        """Boucle heartbeat"""
        while self.running:
            if self.ws:
                await self.send({"action": "ping"})
            await asyncio.sleep(30)

    async def run(self):
        """Boucle principale"""
        self.log("=" * 50)
        self.log("  KOF ULTIMATE ONLINE - BRIDGE")
        self.log("=" * 50)

        while True:
            if not await self.connect():
                self.log("Reconnexion dans 5s...")
                await asyncio.sleep(5)
                continue

            self.running = True

            # Lancer les taches
            tasks = [
                asyncio.create_task(self.receive_loop()),
                asyncio.create_task(self.file_check_loop()),
                asyncio.create_task(self.status_update_loop()),
                asyncio.create_task(self.heartbeat_loop())
            ]

            # Attendre qu'une tache se termine
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

            # Annuler les taches en cours
            for task in pending:
                task.cancel()

            self.log("Deconnecte. Reconnexion dans 5s...")
            await asyncio.sleep(5)

async def main():
    bridge = OnlineBridge()
    await bridge.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBridge arrete")
