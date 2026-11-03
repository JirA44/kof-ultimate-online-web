# Brief d'exécution KOFUO — SupaOlympus + SupaConsciousness

Ce brief transforme les objectifs décidés pour KOFUO en travail vérifiable. Il s'adresse aux agents capables d'inspecter et de modifier les dépôts KOFUO et, lorsqu'ils sont disponibles, d'exécuter le jeu sur des machines de test.

## Règles de travail

1. Commencer par identifier les dépôts, branches, build et composants réellement utilisés. Ne pas supposer que des scripts ou rapports anciens décrivent la version active.
2. Établir un état initial avec chemins/fichiers, étapes de reproduction, captures/logs et sévérité. Ne pas déclarer un correctif ou un test réussi sans preuve.
3. Travailler par lots petits et cohérents. Après chaque correction, relancer le test qui l'a révélée, puis sa régression.
4. Ne pas remplacer les assets ou personnages sous droits incertains et ne pas publier d'assets sans origine/licence vérifiée.
5. Ne pas ouvrir le jeu au public avant le feu vert défini dans [KOFUO_RELEASE_READINESS_FR.md](KOFUO_RELEASE_READINESS_FR.md). Les simulations et analyses d'IA ne valent pas essai réel à deux machines.

## Rôle de SupaOlympus

- Auditer l'architecture et identifier le build réellement joué, les dépendances et les ressources utilisées.
- Implémenter les corrections techniques, l'expérience d'installation, les menus, le roster/encyclopédie et l'intégration du multijoueur.
- Préparer les automatismes de vérification, le déploiement de test, les journaux et les outils de mesure.
- Pour chaque changement, fournir fichier/commit, motif, procédure de reproduction, preuves avant/après, tests exécutés et limites.

## Rôle de SupaConsciousness

- Décomposer chaque objectif en critères observables et scénarios d'échec.
- Chercher activement contradictions, cas limites, régressions visuelles et erreurs de parcours.
- Vérifier indépendamment les résultats d'Olympus et rejouer les scénarios corrigés lorsque le runtime est disponible.
- Tenir le registre des défauts et signaler les inconnues au lieu de les remplir par supposition.

Les deux systèmes travaillent sur le même registre, mais aucun ne s'auto-attribue une validation indépendante. Si l'un a écrit le correctif, l'autre vérifie les critères concernés.

## Objectifs du produit

### 1. Graphismes et lisibilité des personnages

- Améliorer la qualité visuelle générale et la définition des personnages, portraits et sprites.
- Vérifier les personnages en mouvement et en jeu, pas seulement les vignettes.
- Garder une silhouette, des couleurs et une animation lisibles; ne pas appliquer un agrandissement qui crée artefacts, flou ou changements de forme.
- Revoir palette, contrastes et décors pour rendre l'ambiance moins glauque et plus accueillante, tout en restant cohérente avec l'identité du jeu.
- **Retirer ou remplacer les maps glauques**. Tenir un inventaire des arènes, classer les candidates à retirer/remplacer et vérifier toutes les remplaçantes dans des combats réels.

Critère : chaque personnage et chaque map sélectionnables ont été visuellement contrôlés en résolution native et en combat; les défauts de rendu bloquants sont corrigés.

### 2. Menus et sélection des personnages

- Affiner les menus : hiérarchie claire, styles cohérents, navigation clavier/manette prévisible, textes lisibles et retours visuels aux actions.
- Réparer la grille de sélection : dimensions, cases, noms, portraits, défilement, sélection/annulation, limites de roster et correspondance entre case et personnage.
- Vérifier différentes résolutions, mise à l'échelle et configurations d'affichage réellement supportées.

Critère : parcourir le menu de bout en bout et sélectionner chaque personnage prévu; aucune case vide ou incorrecte, aucun blocage ni retour incohérent.

### 3. Encyclopédie intégrée au jeu

- Ajouter une page consultable listant tous les personnages réellement présents dans le roster installé.
- À l'activation d'une carte/fenêtre de personnage, ouvrir sa fiche complète.
- Prévoir nom, présentation, portrait, provenance/version du personnage, style, données utiles en jeu et liste des combos avec commandes exactes.
- Extraire les combos depuis les fichiers de commandes/configuration quand cela est fiable; faire valider ce qui ne peut pas être extrait. Ne jamais inventer un combo.
- Afficher clairement « non documenté » ou « à vérifier » lorsque l'information manque.
- Garder la fiche utilisable à la manette et au clavier, avec retour à la liste sans perdre le contexte.

Critère : chaque personnage du roster a une entrée accessible; chaque combo affiché a une source et a été vérifié en jeu.

### 4. Téléchargement, installation et lancement

- Conserver un parcours principal aussi « tout-en-un » que techniquement et légalement possible : une action pour télécharger, installation guidée, lancement évident.
- Regrouper le jeu, launcher, dépendances redistribuables permises et composants nécessaires lorsque leur inclusion est autorisée et fiable.
- Pour les gros assets qu'on ne peut pas légalement ou pratiquement empaqueter, intégrer un téléchargement guidé avec source autorisée, progression, reprise, vérification d'intégrité et erreurs compréhensibles.
- Vérifier la disponibilité, le contenu et le hash des fichiers du téléchargement principal. Ne jamais appeler « complet » un installateur dont le roster ou les ressources nécessaires manquent.
- Une installation propre doit aller jusqu'au premier combat sans clonage Git ni commandes manuelles.

Critère : un testeur non technique suit le parcours depuis une machine propre jusqu'à un match local; tous les prérequis et limites apparaissent clairement.

### 5. Multijoueur prêt à accueillir des joueurs

- Choisir et documenter une seule architecture de session : serveur public avec matchmaking et lancement de partie réel, ou autre architecture effectivement intégrée.
- Réconcilier le client WebSocket qui pointe vers `localhost:8765`, le guide qui parle d'une connexion Ikemen directe sur le port 7500, et le flow du jeu réel.
- Démontrer que « match trouvé » connecte effectivement les deux jeux, synchronise version/personnages/stages/règles, commence le combat et remonte un résultat cohérent.
- Gérer recherche/annulation, déconnexion, reconnexion, abandon, serveur indisponible, résultats dupliqués et joueurs bloqués en file.
- Mesurer la capacité par paliers avant d'annoncer des nombres; publier la valeur stable mesurée, conditions et date.

Critère : au moins deux ordinateurs indépendants, via le serveur et la configuration destinés à la production, complètent plusieurs parties réelles sans état contradictoire. Puis campagne de charge documentée et reprise après panne.

### 6. Campagne de qualité avant publication

- Utiliser et compléter [KOFUO_RELEASE_READINESS_FR.md](KOFUO_RELEASE_READINESS_FR.md).
- Exécuter les campagnes installation, interface, grille/roster, combats locaux, parties en ligne, charge et reprise.
- Répéter les parcours critiques au minimum dix fois sur le build candidat; diversifier appareils, joueurs, personnages, cartes et conditions réseau.
- Assigner un identifiant à chaque défaut, avec gravité, reproduction, preuve, correctif, version de retest et issue.
- Stopper la diffusion si un défaut critique/majeur reste ouvert, si un parcours critique n'a pas été testé ou si la version vérifiée ne correspond pas à celle distribuée.

Le but est **zéro défaut critique ou majeur connu dans le périmètre validé**, et non une promesse impossible d'absence absolue de tout bug.

## Ordre d'exécution

1. Inventorier les dépôts, runtime, scripts, assets, maps, roster, tests et versions; confirmer ce qui est réellement jouable.
2. Résoudre les bloqueurs de fonctionnement : installation propre, lancement, roster/map, menus, puis architecture réseau/matchmaking.
3. Traiter les améliorations visuelles et menus sur le runtime cible; comparer avant/après et faire contrôler par Consciousness.
4. Construire l'encyclopédie et ses combos à partir de données traçables.
5. Mettre en place une distribution unique/assistée et valider l'intégrité des fichiers.
6. Exécuter campagne complète et charge sur le build candidat; corriger, rejouer, documenter.
7. Rendre une décision explicite : bloqué, préversion fermée ou autorisé à l'ouverture publique.

## Format de chaque rapport Supa

- État : terminé / partiel / bloqué.
- Périmètre et commit exact.
- Objectifs traités et non traités.
- Fichiers modifiés et défauts associés.
- Commandes et environnements réellement utilisés.
- Résultats par scénario, avec liens vers captures/logs/vidéos.
- Retests après correctifs et défauts restants.
- Limites : matériel, joueurs, réseau ou accès indisponibles.
- Décision de sortie selon les critères ci-dessus.

## État actuel connu

La préparation documentaire existe. Les rapports historiques consultés ne démontrent ni matchmaking Internet intégré à une vraie partie à deux machines ni capacité serveur mesurée. L'exécution sur les systèmes Supa et sur le runtime du jeu reste à faire; ce brief ne prétend pas que les agents l'ont déjà exécutée.
