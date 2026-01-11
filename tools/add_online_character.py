#!/usr/bin/env python3
"""
Script pour ajouter le caractère L (ONLINE) à la police Menu Black
"""

import struct
import os
import shutil
from datetime import datetime

def add_character_to_font(font_path, backup=True):
    """Ajoute le caractère L à la table de mapping de la police"""

    print("="*60)
    print("AJOUT DU CARACTERE 'L' (ONLINE) A LA POLICE")
    print("="*60)

    # Vérifier que le fichier existe
    if not os.path.exists(font_path):
        print(f"ERREUR: Fichier non trouvé: {font_path}")
        return False

    # Créer une sauvegarde
    if backup:
        backup_path = font_path + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy(font_path, backup_path)
        print(f"Sauvegarde créée: {backup_path}")

    # Lire le fichier
    with open(font_path, 'rb') as f:
        data = bytearray(f.read())

    print(f"Fichier chargé: {len(data)} octets")

    # Trouver la section [Map]
    map_marker = b'[Map]'
    map_pos = data.find(map_marker)

    if map_pos == -1:
        print("ERREUR: Section [Map] non trouvée")
        return False

    print(f"Section [Map] trouvée à l'offset {map_pos}")

    # Lire le contenu actuel après [Map]
    map_content_start = map_pos + len(map_marker) + 2  # +2 pour \r\n
    current_map = data[map_content_start:].decode('ascii', errors='ignore')

    print(f"\nContenu actuel de [Map]:")
    print(current_map[:500])

    # Vérifier si L existe déjà
    if '\nL ' in current_map or current_map.startswith('L '):
        print("\nLe caractère L existe déjà dans la police!")
        return True

    # Trouver la dernière entrée (K)
    lines = current_map.strip().split('\n')
    last_line = None
    for line in lines:
        line = line.strip()
        if line and line[0] in 'ABCDEFGHIJK':
            last_line = line

    if last_line:
        print(f"\nDernière entrée trouvée: {last_line}")
        parts = last_line.split()
        if len(parts) >= 3:
            last_char = parts[0]
            last_offset = int(parts[1])
            last_width = int(parts[2])

            # Calculer la position pour L
            new_offset = last_offset + last_width
            new_width = last_width  # Même largeur

            print(f"Nouvelle entrée L: offset={new_offset}, width={new_width}")

            # Créer la nouvelle ligne
            new_line = f"L {new_offset} {new_width}\r\n"

            # Trouver où insérer (après K)
            k_line_end = data.find(b'\r\n', data.find(b'K  6400 640', map_pos))
            if k_line_end == -1:
                k_line_end = data.find(b'\n', data.find(b'K ', map_pos))

            if k_line_end != -1:
                insert_pos = k_line_end + 2  # Après \r\n

                # Insérer la nouvelle ligne
                new_data = data[:insert_pos] + new_line.encode('ascii') + data[insert_pos:]

                # Sauvegarder
                with open(font_path, 'wb') as f:
                    f.write(new_data)

                print(f"\nSUCCES! Caractère L ajouté à la police.")
                print(f"Nouvelle taille: {len(new_data)} octets")

                # Vérification
                print(f"\nVérification - Nouvelle fin du fichier:")
                print(new_data[-200:].decode('ascii', errors='ignore'))

                return True

    print("ERREUR: Impossible de trouver la position d'insertion")
    return False


def main():
    font_path = r"D:\KOF Ultimate Online\data\fonts\Menu Black .fnt"

    print("\nCe script va ajouter le caractère 'L' à la table de mapping")
    print("de la police Menu Black .fnt")
    print("\nNote: Le caractère sera mappé mais n'aura pas d'image.")
    print("Il apparaîtra peut-être vide ou avec un placeholder.\n")

    result = add_character_to_font(font_path)

    if result:
        print("\n" + "="*60)
        print("PROCHAINES ETAPES")
        print("="*60)
        print("""
1. Relancer le jeu pour tester
2. Le caractère L devrait maintenant exister dans la police
3. Si l'affichage est vide, il faudra ajouter l'image avec
   Fighter Factory 3 ou un outil similaire

Pour obtenir Fighter Factory 3:
https://fighterfactory.virtualltek.com/
""")
    else:
        print("\nECHEC de l'ajout du caractère")


if __name__ == "__main__":
    main()
