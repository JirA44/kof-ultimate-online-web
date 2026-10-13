# KOFUO — parcours de test joueurs (13 octobre 2026)

**État : scénarios spécifiés, non exécutés.** Ne pas confondre parcours simulés avec joueurs ou comptes réels.

## Persona 1 : nouveau joueur
1. Ouvrir le jeu ; identifier immédiatement Jouer, Tutoriel, Options et Quitter/Retour.
2. Lancer le tutoriel : déplacements, garde, attaques, coups spéciaux, commandes clavier/manette.
3. Choisir un personnage ; comprendre ses forces et commandes.
4. Terminer un combat d'entraînement ; recevoir une explication des erreurs (garde, distance, timing).
5. Revenir au menu sans perdre les réglages.

## Persona 2 : joueur intermédiaire
1. Choisir deux personnages différents et deux arènes.
2. Tester enchaînements, coups spéciaux, hitboxes, dégâts, garde, collisions et IA.
3. Vérifier que les commandes et règles restent cohérentes d'un écran à l'autre.
4. Tester pause/reprise, rematch, changement de personnage et retour menu.
5. Vérifier les performances, les ralentissements et les animations manquantes.

## Persona 3 : joueur qui revient
1. Relancer le jeu après fermeture ; vérifier réglages audio, vidéo et contrôles.
2. Naviguer aux modes de jeu, statistiques et tutoriels déjà parcourus.
3. Tester une déconnexion ou une perte réseau uniquement si un mode en ligne existe réellement.
4. Vérifier que les états d'erreur sont compréhensibles et récupérables.

## Cohérence et qualité graphique
- Audit des menus, nomenclature, ordre des modes, navigation, retour et focus clavier.
- Sprites visibles pour chaque personnage, orientation et animation ; pas de frames transparentes ou de personnages invisibles.
- Vérifier cadrage, échelle, contraste, effets visuels, barres de vie et lisibilité sur les arènes.
- Tester les ressources absentes, les chemins de fichiers et les erreurs de chargement.
- Pour les 188 personnages et 31 arènes annoncés dans le README : validation automatisée des manifestes/ressources, puis échantillonnage visuel et fonctionnel. Ne pas prétendre qu'ils ont été vérifiés.
- Vérifier clavier/manette, ratios d'écran et performances selon les capacités du moteur M.U.G.E.N et de la couche Web.

## Registre de résultats
Pour chaque test : scénario, version/commit, environnement, étapes, attendu, observé, PASS/FAIL/BLOCKED/NOT RUN, capture avant/après et gravité.

## Sécurité
Utiliser des profils fictifs et une installation isolée ; ne pas créer de comptes réels ni déployer en production sans autorisation.
