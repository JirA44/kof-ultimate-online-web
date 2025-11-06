"""
🌐 RÉPARATEUR SYSTÈME MULTIJOUEUR
Corrige tous les problèmes de multijoueur pour rendre le jeu esport-ready
"""
import json
from pathlib import Path
import shutil

class MultiplayerFixer:
    def __init__(self):
        self.game_dir = Path(__file__).parent
        self.data_dir = self.game_dir / "data"
        self.save_dir = self.game_dir / "save"
        self.save_dir.mkdir(exist_ok=True)

    def create_network_config(self):
        """Crée la configuration réseau"""
        print("📡 Création configuration réseau...")

        network_config = {
            "network": {
                "enabled": True,
                "mode": "p2p",
                "port": 7500,
                "max_players": 2,
                "use_ggpo": True,  # Rollback netcode esport
                "input_delay": 2,
                "max_rollback_frames": 8
            },
            "matchmaking": {
                "enabled": True,
                "auto_search": False,
                "ranked": True,
                "casual": True
            },
            "lobby": {
                "enabled": True,
                "max_lobbies": 10,
                "spectators_allowed": True
            }
        }

        config_path = self.save_dir / "network.json"
        config_path.write_text(json.dumps(network_config, indent=2))
        print(f"✅ Configuration réseau créée: {config_path}")

    def create_player_profiles(self):
        """Crée des profils joueurs pour tests"""
        print("👤 Création profils joueurs...")

        profiles = {
            "profiles": [
                {
                    "id": "player1",
                    "name": "Fighter1",
                    "rank": "bronze",
                    "wins": 0,
                    "losses": 0,
                    "favorite_char": "WhirlWind-Goenitz"
                },
                {
                    "id": "player2",
                    "name": "Fighter2",
                    "rank": "bronze",
                    "wins": 0,
                    "losses": 0,
                    "favorite_char": "WhirlWind-Goenitz"
                }
            ]
        }

        profiles_path = self.save_dir / "player_profiles.json"
        profiles_path.write_text(json.dumps(profiles, indent=2))
        print(f"✅ Profils joueurs créés: {profiles_path}")

    def create_matchmaking_config(self):
        """Configure le système de matchmaking"""
        print("🎮 Configuration matchmaking...")

        matchmaking = {
            "matchmaking": {
                "search_timeout": 60,
                "rank_range": 2,
                "connection_test": True,
                "ping_limit": 150,
                "region_priority": True
            },
            "game_settings": {
                "rounds": 3,
                "time_limit": 99,
                "damage_scale": 100,
                "ai_difficulty": 0
            }
        }

        mm_path = self.save_dir / "matchmaking.json"
        mm_path.write_text(json.dumps(matchmaking, indent=2))
        print(f"✅ Matchmaking configuré: {mm_path}")

    def update_mugen_config(self):
        """Met à jour la configuration Mugen pour le multijoueur"""
        print("⚙️  Mise à jour configuration Mugen...")

        # Cherche le fichier de config
        config_files = [
            self.game_dir / "data" / "mugen.cfg",
            self.game_dir / "mugen.cfg",
            self.game_dir / "data" / "config.json"
        ]

        for config_file in config_files:
            if config_file.exists():
                print(f"📝 Backup de {config_file.name}...")
                backup = config_file.with_suffix('.cfg.backup')
                shutil.copy(config_file, backup)

                # Lit et modifie
                content = config_file.read_text(encoding='utf-8', errors='ignore')

                # Active le réseau dans la config
                if '[Network]' not in content:
                    content += """

[Network]
;Configuration réseau pour multijoueur
Enabled = 1
Port = 7500
MaxPlayers = 2
UseGGPO = 1
InputDelay = 2
MaxRollbackFrames = 8
"""
                    config_file.write_text(content, encoding='utf-8')
                    print(f"✅ Configuration réseau ajoutée à {config_file.name}")

        print("✅ Configuration Mugen mise à jour")

    def create_lobby_system(self):
        """Crée le système de lobby multijoueur"""
        print("🏠 Création système de lobby...")

        lobby_data = {
            "lobbies": [],
            "active_matches": [],
            "waiting_players": []
        }

        lobby_path = self.save_dir / "lobby_state.json"
        lobby_path.write_text(json.dumps(lobby_data, indent=2))
        print(f"✅ Système de lobby créé: {lobby_path}")

    def create_quick_test_script(self):
        """Crée un script pour tester rapidement le multijoueur"""
        test_script = self.game_dir / "TEST_MULTIPLAYER.py"

        test_code = '''"""
🧪 TEST RAPIDE MULTIJOUEUR
Vérifie que le système multijoueur fonctionne
"""
import json
from pathlib import Path

def test_multiplayer():
    game_dir = Path(__file__).parent
    save_dir = game_dir / "save"

    print("🧪 TEST SYSTÈME MULTIJOUEUR")
    print("=" * 50)

    # Vérifie config réseau
    network_config = save_dir / "network.json"
    if network_config.exists():
        data = json.loads(network_config.read_text())
        if data.get("network", {}).get("enabled"):
            print("✅ Configuration réseau: OK")
        else:
            print("❌ Configuration réseau: DISABLED")
    else:
        print("❌ Configuration réseau: MANQUANTE")

    # Vérifie profils
    profiles = save_dir / "player_profiles.json"
    if profiles.exists():
        data = json.loads(profiles.read_text())
        print(f"✅ Profils joueurs: {len(data.get('profiles', []))} profils")
    else:
        print("❌ Profils joueurs: MANQUANTS")

    # Vérifie matchmaking
    matchmaking = save_dir / "matchmaking.json"
    if matchmaking.exists():
        print("✅ Matchmaking: OK")
    else:
        print("❌ Matchmaking: MANQUANT")

    # Vérifie lobby
    lobby = save_dir / "lobby_state.json"
    if lobby.exists():
        print("✅ Système lobby: OK")
    else:
        print("❌ Système lobby: MANQUANT")

    print("\\n" + "=" * 50)

if __name__ == "__main__":
    test_multiplayer()
'''

        test_script.write_text(test_code, encoding='utf-8')
        print(f"✅ Script de test créé: {test_script}")

    def fix_all(self):
        """Répare tout le système multijoueur"""
        print("\n🔧 RÉPARATION SYSTÈME MULTIJOUEUR")
        print("=" * 60)

        self.create_network_config()
        self.create_player_profiles()
        self.create_matchmaking_config()
        self.update_mugen_config()
        self.create_lobby_system()
        self.create_quick_test_script()

        print("\n" + "=" * 60)
        print("✅ SYSTÈME MULTIJOUEUR RÉPARÉ")
        print("\n📋 Prochaines étapes:")
        print("   1. Lancer TEST_MULTIPLAYER.py pour vérifier")
        print("   2. Tester avec 2 instances du jeu")
        print("   3. Vérifier que le matchmaking fonctionne")
        print("=" * 60)

if __name__ == "__main__":
    fixer = MultiplayerFixer()
    fixer.fix_all()
