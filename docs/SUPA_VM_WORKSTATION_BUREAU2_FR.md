# Environnement VM isolé pour Supa — bureau de test KOFUO

Statut : **préparation définie; VM non installée/non vérifiée depuis cette session**.

Objectif : fournir à SupaOlympus et SupaConsciousness un environnement de développement et de test KOFUO avec bureau graphique, souris/clavier pilotables, jeu installé et état réinitialisable, sans interrompre le travail de l'utilisateur sur le bureau 1.

## Décision de séparation

Un « bureau 2 » Windows ou une fenêtre VM dans le même compte ne garantit pas à lui seul une saisie indépendante. Une automatisation qui clique dans la fenêtre de la VM peut donner le focus à cette fenêtre et prendre temporairement souris/clavier.

Ordre de préférence pour éviter toute perturbation :

1. **VM dans une session Windows distincte dédiée à Supa**, accessible par console/connexion distante propre, avec environnement et dossier de travail dédiés.
2. Si cette isolation n'est pas disponible : VM sur le bureau 2 avec fenêtre persistante; annoncer que les actions automatisées peuvent prendre le focus brièvement et bloquer les entrées physiques pendant l'action.
3. Si une vraie indépendance de souris/clavier est impérative et non garantie par la session : utiliser un second PC ou une session distante dédiée. Ne pas prétendre qu'un bureau virtuel Windows fournit deux souris indépendantes.

## Inventaire préalable obligatoire

Avant installation, Supa/administrateur doit noter :

- Édition/version de Windows hôte, architecture, mémoire totale, espace libre et modèle GPU.
- État de virtualisation matérielle activée (BIOS/UEFI) et fonctionnalités hyperviseur disponibles.
- Hyperviseur déjà installé et version; présence ou non d'une VM KOFUO antérieure.
- Emplacement actuel des images VM et fichiers projet; aucune suppression ou réinitialisation avant sauvegarde.
- Capacité d'accélération graphique du runtime invité et fréquence d'images constatée dans le jeu.
- Mode de connexion prévu entre Supa, le bureau VM et les sources GitHub.

Ne pas activer/désactiver des composants Windows, modifier BIOS/UEFI, redémarrer, ni écraser une VM existante sans s'arrêter pour organiser ces étapes avec l'utilisateur.

## Configuration cible

- VM Windows 10/11 64 bits compatible avec les outils KOFUO.
- CPU, RAM et disque fixés après inventaire de l'hôte; garder assez de ressources pour que le bureau 1 reste utilisable.
- Disque virtuel extensible avec marge définie; vérifier l'espace avant d'importer les assets volumineux.
- Affichage graphique suffisamment fluide pour tester M.U.G.E.N/Ikemen et capturer les menus/combats.
- Souris et clavier visibles dans la console; résolution définie et reproductible.
- Instantanés : base propre, environnement de développement prêt, build KOFUO candidat.
- Synchronisation versionnée du projet; ne pas partager le profil utilisateur hôte entier avec la VM.

## Isolement et accès fichiers

- Réseau NAT par défaut pour mises à jour et Git. N'exposer aucun port entrant public depuis la VM sans besoin explicite et configuration documentée.
- Partage de dossiers limité au dépôt KOFUO et à un dossier d'échange dédié; pas d'accès aux documents personnels ni aux secrets.
- Ne pas copier de jetons Git, clés API ou fichiers .env de l'hôte. Préférer des identifiants temporaires et à droits minimaux si le projet en a besoin.
- Presse-papiers partagé désactivé par défaut; l'activer uniquement si le workflow le demande.
- Builds et assets non fiables restent dans la VM; points de restauration avant les installations et changements de configuration.
- L'agent ne doit pas accéder aux fichiers d'entreprise ni automatiser l'activité du bureau 1.

## Installation logicielle dans la VM

1. Créer/initialiser l'hyperviseur compatible après inventaire.
2. Créer le compte utilisateur « Supa-KOFUO » sans privilèges administrateur au quotidien.
3. Installer les outils nécessaires au dépôt (Git, runtime et dépendances identifiés par les fichiers du projet).
4. Récupérer une branche de travail dédiée et vérifier le commit.
5. Installer KOFUO par le parcours public candidat; conserver aussi un build de développement distinct.
6. Lancer le jeu, vérifier fenêtre/résolution/son, puis contrôler souris/clavier et capture écran.
7. Prendre un instantané propre après vérification; documenter la procédure de retour arrière.
8. Vérifier que Supa peut lire/écrire le dépôt et produire journaux/captures sans toucher au bureau 1.

Ne pas installer au hasard une chaîne Node/Python ou un moteur différent : inventorier les versions réellement requises par KOFUO et verrouiller celles-ci.

## Critères d'acceptation pour Supa

La VM est déclarée opérationnelle seulement si :

- L'environnement redémarre depuis un instantané documenté.
- Supa peut ouvrir le projet, modifier une branche de travail et générer un build identifiable.
- Le jeu démarre dans la VM et les commandes souris/clavier permettent de naviguer aux menus, sélectionner personnages/maps et jouer un match local.
- Les captures d'écran, journaux et fichiers de défaut sont récupérables dans le dossier d'échange.
- Aucun changement de focus, clic ou saisie d'essai n'est envoyé à une application du bureau 1.
- Un essai d'activité simultanée confirme le niveau réel d'isolation; toute saisie nécessitant le focus hôte est documentée.
- L'installation ne consomme pas des ressources au point de gêner le travail hôte.
- Les fonctions et accès accordés aux agents sont listés et limités au nécessaire.

## Checklist de mise en service

- [ ] Inventaire hôte/hyperviseur réalisé
- [ ] Choix session indépendante ou limitation du « bureau 2 » documentée
- [ ] Ressources CPU/RAM/disque disponibles estimées
- [ ] Hyperviseur installé/vérifié
- [ ] VM créée sans écraser d'instance existante
- [ ] OS invité installé et mis à jour
- [ ] Souris, clavier, affichage et capture vérifiés
- [ ] Réseau et dossiers partagés limités
- [ ] Outils de dev correspondant au dépôt installés
- [ ] Projet KOFUO cloné sur branche de travail et version consignée
- [ ] Jeu lancé, navigation et combat local testés
- [ ] Journaux/captures exportables
- [ ] Instantané et procédure de restauration vérifiés
- [ ] Test d'absence d'interférence avec le bureau 1 exécuté
- [ ] Accès donné à SupaOlympus et SupaConsciousness limité et vérifié

## État constaté dans cette session

Aucune fenêtre VM ou logiciel de virtualisation n'apparaissait dans l'inventaire UI accessible. La vérification système PowerShell a été refusée par l'environnement. Cela ne permet pas de conclure si une VM existe ailleurs, si l'hyperviseur est installé, ou si l'option matérielle est active. Les cases restent donc non cochées jusqu'à vérification sur l'hôte.
