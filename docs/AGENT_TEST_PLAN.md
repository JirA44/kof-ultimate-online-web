# KOFUO — Instructions aux agents testeurs (13 octobre 2026)

## Objectif
Tester réellement KOF Ultimate Online, reproduire les bugs, proposer des correctifs minimaux et refaire les tests. Ne jamais annoncer « fonctionnel » sur la seule base d'une lecture du code.

## Périmètre et composants
- Dépôt : JirA44/kof-ultimate-online-web
- Références : FULL_TEST.py, matchmaking_server.py, matchmaking_client.py, virtual_players_ai.py, matchmaking_elo.py, multiplayer_menu.py.
- Environnement : machine de test isolée, jeu installé, port local 9999; pas de serveur public ni de vrais comptes.

## Agent A — exécution
1. Inventorier dépendances et commandes de lancement, noter version Python, OS, commit et prérequis manquants.
2. Exécuter les tests existants et enregistrer stdout/stderr, codes de sortie et durées.
3. Lancer le serveur sur 127.0.0.1 avec un port de test libre; démarrer deux clients simulés distincts. Vérifier connexions, file rapide et classée, appariement unique, démarrage, fin et nettoyage du match.
4. Tester clients simultanés, doublons d'identité, messages invalides, trames TCP partielles, déconnexion avant/après appariement, timeout, reconnexion, arrêt du serveur.
5. Vérifier classement, historique, persistance et séparation des profils. Vérifier le jeu réellement jouable et la synchronisation uniquement si le moteur et les clients sont disponibles.
6. Éviter les opérations destructives; utiliser des données temporaires. Ne pas considérer des joueurs virtuels comme preuve d'une partie jouable.

## Agent B — correction
Pour chaque échec confirmé, créer une issue ou un correctif sur une branche séparée avec test de non-régression. Ne jamais modifier les sauvegardes utilisateur ni déclencher de déploiement en production. Ne pas fusionner automatiquement.

## Agent C — validation indépendante
Relancer les scénarios sur le correctif et vérifier les régressions. Classer chaque résultat PASS, FAIL, BLOCKED ou NOT RUN, sans transformer BLOCKED en PASS.

## Rapport obligatoire
Créer un rapport horodaté (Markdown + JSON si possible) avec :
- commit testé, environnement, commandes exactes, logs et traces;
- scénario, résultat attendu, résultat observé, durée;
- sévérité P0 à P3, reproduction, cause probable, correctif/PR, retest;
- couverture réellement exécutée, éléments non testables et décision « prêt / non prêt ».
Une erreur réseau ou une dépendance absente est un blocage, pas un succès.

## Ordre de priorité
P0 : corruption de données, accès non autorisé, crash systématique.
P1 : impossible de se connecter, d'apparier deux joueurs ou de terminer une partie.
P2 : reconnexion, classement, désynchronisation intermittente.
P3 : affichage et ergonomie.

## Critère de sortie
Aucune validation de la plateforme sans une session de jeu à deux clients réellement exécutée, des preuves de synchronisation, et les tests critiques verts. Si l'exécution locale est inaccessible, livrer les scripts/tests et marquer l'exécution BLOCKED.
