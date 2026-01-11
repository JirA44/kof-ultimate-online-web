#!/usr/bin/env python3
"""
Analyseur et éditeur de polices Elecbyte FNT pour IKEMEN/MUGEN
KOF Ultimate Online - Outil pour ajouter ONLINE au menu
"""

import struct
import os
from PIL import Image
import io

class ElecbyteFontAnalyzer:
    def __init__(self, filepath):
        self.filepath = filepath
        self.data = None
        self.header = {}
        self.characters = {}

    def load(self):
        """Charge le fichier FNT"""
        with open(self.filepath, 'rb') as f:
            self.data = f.read()
        print(f"Fichier chargé: {len(self.data)} octets")

    def analyze_header(self):
        """Analyse l'en-tête du fichier"""
        # Signature ElecbyteFnt
        sig = self.data[:12].decode('ascii', errors='ignore')
        print(f"Signature: {sig}")

        # Version
        version = struct.unpack('<I', self.data[12:16])[0]
        print(f"Version: {version}")

        # Offset vers les données
        offset1 = struct.unpack('<I', self.data[16:20])[0]
        print(f"Offset données: {offset1}")

        # Taille des données (estimation)
        if len(self.data) > 20:
            offset2 = struct.unpack('<I', self.data[20:24])[0]
            print(f"Offset 2: {offset2}")

        self.header = {
            'signature': sig,
            'version': version,
            'data_offset': offset1
        }

    def find_character_table(self):
        """Cherche la table des caractères"""
        # Dans le format Elecbyte, les caractères sont mappés
        # Cherchons les patterns de caractères ASCII

        print("\nRecherche de la table des caractères...")

        # Chercher où les données de caractères commencent
        offset = self.header.get('data_offset', 72)

        # Lire les données à partir de l'offset
        print(f"\nDonnées à l'offset {offset}:")
        chunk = self.data[offset:offset+100]
        print(f"Hex: {chunk[:50].hex()}")

        # Essayer de trouver la structure
        # Format FNT v2: chaque caractère a une entrée avec position, taille, etc.

    def extract_character_info(self):
        """Extrait les informations sur chaque caractère"""
        print("\nExtraction des caractères...")

        # Le format Elecbyte FNT peut avoir différentes structures
        # Essayons de trouver les caractères A-K utilisés par le menu

        for char in 'ABCDEFGHIJK':
            # Chercher le caractère dans les données
            ascii_val = ord(char)
            print(f"Caractère '{char}' (ASCII {ascii_val})")

    def scan_for_sprites(self):
        """Scanne le fichier pour trouver les sprites PCX/images"""
        print("\nRecherche de sprites intégrés...")

        # Les polices MUGEN peuvent contenir des sprites PCX
        # Signature PCX: premier octet = 0x0A

        pcx_positions = []
        for i in range(len(self.data) - 4):
            if self.data[i] == 0x0A and self.data[i+1] in [0, 2, 3, 4, 5]:
                # Potentiel header PCX
                if self.data[i+2] == 1:  # encoding
                    pcx_positions.append(i)

        print(f"Positions PCX potentielles trouvées: {len(pcx_positions)}")
        if pcx_positions[:10]:
            print(f"Premières positions: {pcx_positions[:10]}")

    def get_full_structure(self):
        """Analyse complète de la structure"""
        print("\n" + "="*60)
        print("ANALYSE COMPLETE DE LA POLICE")
        print("="*60)

        self.load()
        self.analyze_header()
        self.find_character_table()
        self.extract_character_info()
        self.scan_for_sprites()

        # Afficher un dump hex des premières parties du fichier
        print("\n" + "-"*60)
        print("DUMP HEXADECIMAL (premiers 512 octets)")
        print("-"*60)

        for i in range(0, min(512, len(self.data)), 16):
            hex_part = ' '.join(f'{b:02x}' for b in self.data[i:i+16])
            ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in self.data[i:i+16])
            print(f"{i:04x}: {hex_part:<48} {ascii_part}")


def main():
    font_path = r"D:\KOF Ultimate Online\data\fonts\Menu Black .fnt"

    if not os.path.exists(font_path):
        print(f"Fichier non trouvé: {font_path}")
        return

    analyzer = ElecbyteFontAnalyzer(font_path)
    analyzer.get_full_structure()

    print("\n" + "="*60)
    print("PROCHAINES ETAPES")
    print("="*60)
    print("""
Pour ajouter 'ONLINE' au menu, nous devons:
1. Comprendre le format exact des caractères dans cette police
2. Créer une image pour 'ONLINE' similaire aux autres boutons
3. Ajouter cette image comme caractère 'L' dans la police

Options:
- Utiliser Fighter Factory 3 (outil graphique)
- Créer un script Python pour modifier directement le fichier
""")


if __name__ == "__main__":
    main()
