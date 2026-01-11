#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO FIX MULTIPLAYER - Réparation automatique du système multijoueur
Configure automatiquement le système réseau
"""

import os
import sys
from pathlib import Path
from datetime import datetime

class MultiplayerFixer:
    """Réparateur système multijoueur"""

    def __init__(self):
        self.base_path = Path(r"D:\KOF Ultimate Online kofuo Online kofuo kofuo Online kofuo")
        self.data_path = self.base_path / "data"
        self.mugen_cfg = self.data_path / "mugen.cfg"
        self.backup_path = self.base_path / "config_backup"

    def log(self, message, level="INFO"):
        """Log avec icônes"""
        icons = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "FIX": "🔧"
        }
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {icons.get(level, '')} {message}")

    def create_backup(self):
        """Créer backup de la config"""
        self.log("Création backup de mugen.cfg...", "INFO")

        if not self.mugen_cfg.exists():
            self.log("mugen.cfg introuvable!", "ERROR")
            return False

        self.backup_path.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_path / f"mugen.cfg.backup_{timestamp}"

        try:
            import shutil
            shutil.copy2(self.mugen_cfg, backup_file)
            self.log(f"Backup créé: {backup_file.name}", "SUCCESS")
            return True
        except Exception as e:
            self.log(f"Erreur backup: {e}", "ERROR")
            return False

    def check_network_section(self):
        """Vérifier si la section Network existe"""
        try:
            content = self.mugen_cfg.read_text(encoding='latin-1', errors='ignore')
            return '[Network]' in content or '[network]' in content
        except Exception as e:
            self.log(f"Erreur lecture config: {e}", "ERROR")
            return False

    def add_network_config(self):
        """Ajouter la configuration réseau"""
        self.log("Ajout configuration réseau...", "FIX")

        network_config = """

;---------------------------------------------------------------------------
; Network Configuration (Added by AUTO_FIX_MULTIPLAYER)
;---------------------------------------------------------------------------
[Network]
; Enable network play
Enabled = 1

; Server settings
Server = 127.0.0.1
Port = 9999

; Maximum players (2 for 1v1 fighting game)
MaxPlayers = 2

; Netplay settings
Netplay = 1

; Rollback netcode frames (lower = less lag but requires better connection)
; Recommended: 2-4 for local network, 4-8 for internet
RollbackFrames = 4

; Input delay frames (can help with timing)
InputDelay = 0

; Synchronization check interval (frames)
SyncCheck = 60

; Disconnect timeout (seconds)
Timeout = 30

; Debug network (0=off, 1=on)
DebugNetwork = 0

; Quality of Service settings
QoS = 1

; Bandwidth limit (KB/s, 0=unlimited)
BandwidthLimit = 0

; Packet size optimization
PacketSize = 1024

;---------------------------------------------------------------------------

"""

        try:
            # Lire le contenu actuel
            content = self.mugen_cfg.read_text(encoding='latin-1', errors='ignore')

            # Ajouter la config réseau à la fin
            new_content = content + network_config

            # Écrire le nouveau contenu
            self.mugen_cfg.write_text(new_content, encoding='latin-1', errors='ignore')

            self.log("Configuration réseau ajoutée avec succès!", "SUCCESS")
            return True

        except Exception as e:
            self.log(f"Erreur ajout config: {e}", "ERROR")
            return False

    def verify_matchmaking_files(self):
        """Vérifier les fichiers de matchmaking"""
        self.log("Vérification fichiers matchmaking...", "INFO")

        files_to_check = {
            "matchmaking_server.py": "Serveur matchmaking",
            "matchmaking_client.py": "Client matchmaking",
            "matchmaking_server_pro.py": "Serveur pro (optionnel)"
        }

        all_good = True
        for filename, description in files_to_check.items():
            filepath = self.base_path / filename
            if filepath.exists():
                self.log(f"✓ {description}: TROUVÉ", "SUCCESS")
            else:
                self.log(f"✗ {description}: MANQUANT", "WARNING")
                if "optionnel" not in description:
                    all_good = False

        return all_good

    def test_network_config(self):
        """Tester la configuration réseau"""
        self.log("Test de la configuration réseau...", "INFO")

        try:
            import socket

            # Tester si le port est disponible
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.settimeout(2)

            try:
                # Essayer de se connecter au port (devrait échouer si rien n'écoute)
                result = test_socket.connect_ex(('127.0.0.1', 9999))
                if result == 0:
                    self.log("⚠️ Port 9999 déjà utilisé", "WARNING")
                else:
                    self.log("✓ Port 9999 disponible", "SUCCESS")
            finally:
                test_socket.close()

            return True

        except Exception as e:
            self.log(f"Erreur test réseau: {e}", "ERROR")
            return False

    def fix_all(self):
        """Réparer tout le système multijoueur"""
        print("\n" + "="*60)
        print("RÉPARATION SYSTÈME MULTIJOUEUR")
        print("="*60 + "\n")

        success = True

        # 1. Créer backup
        if not self.create_backup():
            success = False

        # 2. Vérifier si Network existe déjà
        if self.check_network_section():
            self.log("Section [Network] existe déjà!", "INFO")
            self.log("Aucune modification nécessaire", "SUCCESS")
        else:
            # Ajouter la configuration
            if not self.add_network_config():
                success = False

        # 3. Vérifier fichiers matchmaking
        if not self.verify_matchmaking_files():
            self.log("⚠️ Certains fichiers matchmaking sont manquants", "WARNING")

        # 4. Tester la config
        self.test_network_config()

        print("\n" + "="*60)
        if success:
            self.log("Réparation multijoueur terminée avec succès!", "SUCCESS")
        else:
            self.log("Réparation terminée avec des erreurs", "WARNING")
        print("="*60 + "\n")

        return success

    def display_info(self):
        """Afficher les informations de configuration"""
        print("\n📊 CONFIGURATION RÉSEAU")
        print("-" * 60)
        print("Serveur:        127.0.0.1 (localhost)")
        print("Port:           9999")
        print("Joueurs max:    2")
        print("Rollback:       4 frames")
        print("Netplay:        Activé")
        print("-" * 60)
        print("\n💡 Pour démarrer le serveur:")
        print("   python matchmaking_server.py")
        print("\n💡 Pour tester:")
        print("   1. Lancez le serveur dans un terminal")
        print("   2. Lancez le jeu")
        print("   3. Sélectionnez mode Online/Network")
        print("-" * 60 + "\n")


def main():
    """Point d'entrée principal"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*12 + "AUTO FIX MULTIPLAYER v1.0" + " "*21 + "║")
    print("║" + " "*8 + "Réparation automatique système réseau" + " "*13 + "║")
    print("╚" + "="*58 + "╝")
    print("\n")

    fixer = MultiplayerFixer()

    # Demander confirmation
    print("⚠️  Ce script va modifier votre fichier mugen.cfg")
    print("   Un backup sera créé automatiquement.\n")

    choice = input("Continuer? (O/N): ").strip().upper()

    if choice != 'O':
        print("\n❌ Opération annulée par l'utilisateur\n")
        return

    print("\n")

    # Lancer la réparation
    success = fixer.fix_all()

    # Afficher les infos
    if success:
        fixer.display_info()

    print("\n✅ Opération terminée!")
    print("\n💡 Conseil: Relancez l'audit qualité pour vérifier:")
    print("   python ESPORT_QUALITY_MONITOR.py\n")


if __name__ == "__main__":
    main()
