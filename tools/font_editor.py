#!/usr/bin/env python3
"""
Editeur de polices Elecbyte FNT pour IKEMEN/MUGEN
Permet d'ajouter le caractère ONLINE au menu
"""

import struct
import os
import sys

class ElecbyteFontEditor:
    def __init__(self, filepath):
        self.filepath = filepath
        self.data = bytearray()

    def load(self):
        """Charge le fichier FNT"""
        with open(self.filepath, 'rb') as f:
            self.data = bytearray(f.read())
        print(f"Police chargée: {len(self.data)} octets")
        return True

    def analyze_structure(self):
        """Analyse la structure détaillée du fichier"""
        print("\n=== STRUCTURE DU FICHIER ===")

        # Header Elecbyte
        sig = self.data[:12].decode('ascii', errors='ignore')
        version = struct.unpack('<I', self.data[12:16])[0]

        # Offsets importants
        pcx_offset = struct.unpack('<I', self.data[16:20])[0]
        text_offset = struct.unpack('<I', self.data[20:24])[0]
        map_offset = struct.unpack('<I', self.data[24:28])[0]

        print(f"Signature: {sig}")
        print(f"Version: {version}")
        print(f"Offset PCX: {pcx_offset}")
        print(f"Offset texte: {text_offset}")
        print(f"Offset map: {map_offset}")

        # Chercher la table de mapping des caractères
        # Dans FNT v2, après le PCX il y a une table de caractères

        # Lire le texte du créateur
        creator_start = 0x20
        creator_end = self.data.find(b'\x00', creator_start)
        creator = self.data[creator_start:creator_end].decode('ascii', errors='ignore')
        print(f"Créateur: {creator}")

        return {
            'signature': sig,
            'version': version,
            'pcx_offset': pcx_offset,
            'text_offset': text_offset,
            'map_offset': map_offset
        }

    def find_character_map(self):
        """Trouve la table de mapping des caractères"""
        print("\n=== RECHERCHE TABLE DES CARACTERES ===")

        # La table de caractères est généralement à la fin du fichier
        # Format: pour chaque caractère, offset vers le sprite

        # Chercher à partir de la fin
        end_offset = len(self.data)

        # Lire les derniers octets pour trouver la structure
        print(f"\nDerniers 256 octets du fichier:")
        last_bytes = self.data[-256:]

        # Afficher en hex
        for i in range(0, len(last_bytes), 32):
            chunk = last_bytes[i:i+32]
            hex_str = ' '.join(f'{b:02x}' for b in chunk)
            print(f"  {hex_str}")

        # Chercher des patterns de mapping (offsets répétitifs)
        # Dans les polices Elecbyte, il y a souvent une table à la fin

        # Vérifier l'offset du texte (text_offset)
        text_offset = struct.unpack('<I', self.data[20:24])[0]
        if text_offset < len(self.data):
            print(f"\nContenu à text_offset ({text_offset}):")
            text_data = self.data[text_offset:text_offset+100]
            print(f"  {text_data[:50]}")

    def extract_pcx_info(self):
        """Extrait les informations du sprite PCX intégré"""
        print("\n=== INFO SPRITE PCX ===")

        pcx_offset = struct.unpack('<I', self.data[16:20])[0]

        if pcx_offset >= len(self.data):
            print("Offset PCX invalide")
            return None

        # Header PCX
        pcx_header = self.data[pcx_offset:pcx_offset+128]

        manufacturer = pcx_header[0]
        version = pcx_header[1]
        encoding = pcx_header[2]
        bpp = pcx_header[3]

        xmin = struct.unpack('<H', pcx_header[4:6])[0]
        ymin = struct.unpack('<H', pcx_header[6:8])[0]
        xmax = struct.unpack('<H', pcx_header[8:10])[0]
        ymax = struct.unpack('<H', pcx_header[10:12])[0]

        width = xmax - xmin + 1
        height = ymax - ymin + 1

        print(f"Manufacturer: {manufacturer}")
        print(f"Version PCX: {version}")
        print(f"Encoding: {encoding}")
        print(f"Bits par pixel: {bpp}")
        print(f"Dimensions: {width} x {height}")
        print(f"Bounds: ({xmin},{ymin}) - ({xmax},{ymax})")

        return {
            'offset': pcx_offset,
            'width': width,
            'height': height,
            'bpp': bpp
        }

    def list_defined_characters(self):
        """Liste les caractères définis dans la police"""
        print("\n=== CARACTERES DEFINIS ===")

        # Dans le format FNT, la table de mapping est après le PCX
        # Chaque entrée contient: caractère ASCII, offset X, largeur

        map_offset = struct.unpack('<I', self.data[24:28])[0]

        if map_offset == 0 or map_offset >= len(self.data):
            # Essayer de trouver la table autrement
            # Chercher après le PCX data
            print("Recherche alternative de la table...")

            # Le format semble avoir la table à text_offset
            text_offset = struct.unpack('<I', self.data[20:24])[0]

            if text_offset < len(self.data):
                print(f"Analyse à l'offset {text_offset}:")

                # Lire les données
                pos = text_offset
                count = 0
                while pos < len(self.data) - 4 and count < 50:
                    byte = self.data[pos]
                    if 32 <= byte < 127:
                        char = chr(byte)
                        print(f"  Position {pos}: caractère '{char}' (0x{byte:02x})")
                        count += 1
                    pos += 1

    def get_summary(self):
        """Affiche un résumé complet"""
        print("\n" + "="*60)
        print("RESUME DE L'ANALYSE")
        print("="*60)

        info = self.analyze_structure()
        pcx_info = self.extract_pcx_info()
        self.find_character_map()

        print("\n" + "="*60)
        print("SOLUTION PROPOSEE")
        print("="*60)
        print("""
Le fichier Menu Black .fnt contient un sprite PCX avec tous les
caractères de menu (A-K) disposés en grille.

Pour ajouter 'ONLINE':
1. Extraire l'image PCX du fichier
2. Ajouter un caractère 'L' avec le texte 'ONLINE'
3. Mettre à jour la table de mapping
4. Reconstruire le fichier FNT

Alternative plus simple:
- Télécharger Fighter Factory 3 (gratuit)
- Ouvrir Menu Black .fnt
- Ajouter manuellement le caractère L
- Sauvegarder

Voulez-vous que je génère une image PNG 'ONLINE' que vous
pourrez importer manuellement avec Fighter Factory?
""")


def main():
    font_path = r"D:\KOF Ultimate Online\data\fonts\Menu Black .fnt"

    if not os.path.exists(font_path):
        print(f"Fichier non trouvé: {font_path}")
        return

    editor = ElecbyteFontEditor(font_path)
    editor.load()
    editor.get_summary()


if __name__ == "__main__":
    main()
