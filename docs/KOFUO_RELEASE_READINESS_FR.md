# KOFUO — Porte de validation avant ouverture au public

État : **préparation requise — aucune validation de lancement public établie par ce document**  
Portée : installation, jeu, interface, roster, matchmaking, sessions réseau, capacité et exploitation.

## Règle de lancement

KOFUO ne passe en lancement public que lorsque chaque parcours critique a été exécuté sur une version identifiée, que les preuves sont conservées, que les défauts bloquants sont corrigés et retestés, et qu'aucun défaut critique ou majeur connu ne reste ouvert.

« Aucun problème détecté » signifie aucun problème trouvé dans la campagne documentée. Cela ne garantit pas l'absence absolue de bugs.

## Constat à vérifier avant la campagne

Les documents du dépôt décrivent plusieurs voies qui ne sont pas encore démontrées comme un seul service cohérent :

- `BATTLENET_CLIENT.py` se connecte par défaut à `ws://localhost:8765`.
- `GUIDE_MULTIJOUEUR.md` décrit plutôt une connexion directe Ikemen GO sur le port 7500, avec redirection de port, VPN ou Parsec.
- Le client de matchmaking annonce un match trouvé, mais les éléments consultés ne démontrent pas que la session démarre ensuite une partie Ikemen GO avec les deux joueurs.
- Le fichier `test_report.json` daté du 1er janvier 2026 annonce 25 contrôles réussis, mais vérifie surtout la présence de fichiers et de composants. Il ne prouve pas une partie en ligne réelle ni une charge concurrente.
- Le rapport d'octobre 2025 mentionne des tests de navigation et de sélection, mais note l'échec des captures d'écran. Il ne constitue pas une preuve visuelle complète.

Ces points doivent être confirmés ou corrigés dans le code et la configuration actuels avant toute annonce de compatibilité multijoueur publique.

## Mission des deux systèmes

### SupaOlympus — intégration et validation technique

- Cartographier le démarrage depuis l'installateur jusqu'au premier match.
- Vérifier les chemins, versions, assets, roster, stages, launcher et configuration réseau.
- Construire les tests reproductibles : installation propre, lancement, sélection, combat local, connexion, matchmaking, démarrage du match, fin de match et reconnexion.
- Mesurer la capacité du serveur par paliers, avec limites et seuils d'arrêt définis avant l'essai.
- Produire les journaux, captures, versions, commandes, résultats et défauts reproductibles.
- Corriger les défauts techniques après confirmation de leur reproduction et relancer les tests concernés.

### SupaConsciousness — cohérence, scénarios et contre-vérification

- Générer des scénarios normaux, limites et adverses pour chaque étape du parcours.
- Chercher les incohérences entre page web, installateur, launcher, client, version du jeu, roster et serveur.
- Contrôler les états d'erreur et de reprise : serveur absent, coupure réseau, annulation de recherche, joueur quittant, double connexion, données invalides et session bloquée.
- Rejouer les scénarios après correction et comparer les résultats aux critères d'acceptation.
- Signaler explicitement les hypothèses, tests impossibles à exécuter et zones non couvertes.

Les deux systèmes peuvent analyser, proposer et exécuter les vérifications disponibles. Une synthèse d'IA ou un test simulé ne remplace pas une vraie partie avec deux installations distinctes et deux joueurs.

## Campagne obligatoire

1. **Installation**
   - Machine propre, téléchargement depuis le bouton principal, vérification d'intégrité, installation, premier lancement, mise à jour et désinstallation/réinstallation.
   - Tester les permissions Windows, antivirus, chemins avec espaces/accents, manque d'espace et téléchargement interrompu.
   - Résultat attendu : aucun fichier essentiel manquant; messages compréhensibles et procédure de récupération.

2. **Interface et contenu**
   - Parcourir chaque menu, retour arrière, navigation clavier/manette, affichage à plusieurs résolutions.
   - Parcourir toutes les cases du roster et toutes les arènes sélectionnables.
   - Vérifier portraits, sprites, noms, fiches, combos, collisions, éléments manquants et cohérence de l'ambiance visuelle.
   - Résultat attendu : aucun élément inaccessible, superposé, illisible, manquant ou incohérent.

3. **Jeu local**
   - Jouer des matchs complets avec plusieurs personnages et stages, clavier et manette, pause, reprise, rematch et sortie.
   - Vérifier commandes, animations, son, barres de vie, détection de victoire, transitions et journaux.
   - Résultat attendu : pas de crash, blocage, softlock ni défaut empêchant de jouer.

4. **Multijoueur réel**
   - Deux machines et deux installations indépendantes; test LAN puis Internet sur le serveur réellement prévu.
   - Connexion, authentification, présence, recherche, annulation, match trouvé, chargement du même combat, commandes des deux joueurs, fin, résultat, classement et rematch.
   - Refaire les parcours avec latence, perte de paquets, déconnexion/reconnexion et fermeture brutale d'un client.
   - Résultat attendu : chaque transition est confirmée des deux côtés; le client ne reste pas faussement « connecté » ou « en match ».

5. **Charge et exploitation**
   - Définir la capacité cible avant le test, puis augmenter progressivement les connexions simultanées.
   - Mesurer connexions, joueurs en file, matchs actifs, latence, erreurs, mémoire, CPU, redémarrage et récupération après panne.
   - Arrêter le palier si les seuils prédéfinis sont dépassés; ne jamais publier un nombre de joueurs non mesuré.
   - Résultat attendu : capacité publiée limitée au dernier palier stable reproduit.

6. **Répétition et régression**
   - Exécuter au moins 10 cycles complets installation → match réel → fin → reconnexion sur la version candidate; toute correction d'un défaut critique ou majeur relance la campagne concernée.
   - Inclure plusieurs machines, comptes, personnages, stages, périphériques et conditions réseau.
   - Conserver un rapport distinct par exécution et par build; ne pas remplacer les anciens résultats.

## Registre de campagne

Pour chaque exécution, consigner :

| Champ | Valeur requise |
|---|---|
| Identifiant de campagne | Date, numéro d'exécution |
| Version testée | Commit, version du jeu, version du serveur |
| Environnement | OS, matériel, réseau, résolution, périphériques |
| Scénarios | Identifiants des tests exécutés et non exécutés |
| Résultats | Réussite/échec par scénario, durée et mesures |
| Preuves | Journaux, captures, vidéo si utile, configuration expurgée |
| Défauts | Identifiant, gravité, étapes de reproduction, responsable |
| Retest | Version corrigée et résultat du retest |
| Décision | Bloqué ou autorisé pour l'étape suivante, avec justification |

## Seuils de décision

- **Bloqué** : un défaut critique ou majeur ouvert; parcours multijoueur non démontré sur deux machines; serveur public absent ou non configuré; données de charge manquantes; version testée différente de celle publiée.
- **Préversion fermée** : parcours essentiels validés et défauts résiduels explicitement documentés; accès limité à un groupe de test.
- **Ouverture publique** : campagne complète répétée sur le build candidat, aucun défaut critique/majeur ouvert, sauvegarde des preuves, capacité réelle mesurée, procédure de surveillance et de retour arrière disponible.

## Statut actuel

**Bloqué — préparation et preuves manquantes.** Les rapports historiques du dépôt ne démontrent pas le parcours multijoueur Internet de bout en bout ni la capacité en charge. Aucune campagne décrite ici n'a été exécutée par l'ajout de ce document.
