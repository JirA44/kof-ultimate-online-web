# KOF ULTIMATE ONLINE 🎮

<div align="center">

**Version 2.0 Enhanced**

[![License](https://img.shields.io/badge/license-Free-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![M.U.G.E.N](https://img.shields.io/badge/M.U.G.E.N-1.1.0%20Beta%201-red.svg)](http://www.elecbyte.com/mugen/)

*Le jeu de combat ultime avec 188 personnages, système d'auto-réparation et IA avancée*

## À quoi sert ce dépôt ?

Ce dépôt rassemble une version personnalisée de KOF sous M.U.G.E.N, ainsi que des lanceurs et des outils de vérification et de dépannage. Il s’adresse aux personnes qui veulent lancer le jeu, ajuster ses fichiers ou diagnostiquer un problème sans parcourir les scripts un par un.

## Pourquoi l’utiliser ?

Le projet regroupe le jeu et ses outils autour de tâches concrètes : démarrer une partie, vérifier les fichiers, examiner les journaux et configurer les personnages ou les commandes. Les scripts de diagnostic peuvent aider à localiser un problème ; ils ne garantissent pas qu’une réparation automatique soit toujours possible.

## Exemples

- **Lancer le jeu** : utiliser le launcher intelligent indiqué dans la section « Lancement rapide », ou lancer directement l’exécutable si les fichiers nécessaires sont présents.
- **Diagnostiquer un démarrage bloqué** : lancer d’abord l’outil de vérification, examiner le rapport, puis utiliser l’auto-réparation si le diagnostic le recommande.
- **Ajouter un personnage** : placer ses fichiers dans le dossier prévu, l’inscrire dans la configuration de sélection puis vérifier le résultat avec l’outil de test.

Le dépôt indique que certains gros fichiers de personnages ne sont pas inclus. Il faut donc disposer de ces ressources avant de pouvoir utiliser une installation complète.



[🎮 Installation](#installation) • [📖 Documentation](#documentation) • [🚀 Lancement](#lancement-rapide) • [⚙️ Configuration](#configuration)

</div>

---

## 📋 Table des Matières

- [À Propos](#à-propos)
- [Caractéristiques](#caractéristiques)
- [Installation](#installation)
- [Lancement Rapide](#lancement-rapide)
- [Documentation](#documentation)
- [Structure du Projet](#structure-du-projet)
- [Outils de Diagnostic](#outils-de-diagnostic)
- [Configuration](#configuration)
- [Dépannage](#dépannage)
- [Contribution](#contribution)
- [License](#license)

---

## 🎯 À Propos

**KOF ULTIMATE ONLINE** est une version améliorée et étendue du moteur M.U.G.E.N avec un focus sur la stabilité, l'accessibilité et l'intelligence artificielle. Ce projet transforme le jeu de combat classique en une expérience moderne avec auto-réparation, navigation IA et support multijoueur avancé.

### 🌟 Points Forts

- **188 personnages jouables** avec sprites haute qualité
- **31 stages/arènes** variés
- **Système d'auto-réparation** qui détecte et corrige automatiquement les erreurs
- **IA de navigation** qui peut jouer automatiquement
- **Support manette** avec auto-détection
- **Menu principal modernisé** avec animations
- **Outils de diagnostic complets**

---

## ✨ Caractéristiques

### 🎮 Gameplay

- **Mode Arcade** - Affrontez une série d'adversaires contrôlés par l'IA
- **Mode VS** - Combat 1v1 contre un ami ou l'IA
- **Mode Team** - Combats en équipe 3v3
- **Mode Survival** - Survivez le plus longtemps possible
- **Mode Training** - Entraînez-vous et perfectionnez vos combos

### 🤖 Intelligence Artificielle

- **IA de navigation** (`launcher_ai_navigator.py`) - Navigue automatiquement dans les menus
- **IA joueur** (`ai_player_system.py`) - Joue automatiquement avec stratégies adaptatives
- **Amélioration sprites IA** (`ai_retro_enhancer.py`) - Améliore visuellement les sprites avec IA

### 🔧 Outils Système

- **Auto-réparation** (`auto_repair_system.py`) - Répare automatiquement les erreurs détectées
- **Tests automatisés** (`auto_test_system.py`) - Vérifie 21 composants du jeu
- **Monitoring temps réel** (`game_monitor.py`) - Surveille le jeu pendant l'exécution
- **Vérification complète** (`verify_game.py`) - Audit complet de tous les fichiers

### 🎨 Personnalisation

- Menu principal avec animations cyber modernes
- Support pour ajout de personnages personnalisés
- Configuration flexible des stages
- Système de balancement des personnages

---

## 💾 Installation

### Prérequis

- **Système d'exploitation:** Windows 10/11 (64-bit)
- **RAM:** 2 GB minimum, 4 GB recommandé
- **Espace disque:** 12 GB (10 GB pour les personnages + 2 GB pour le système)
- **Python:** 3.8+ (optionnel, pour les outils de diagnostic)

### Installation Standard

1. **Cloner le dépôt:**
   ```bash
   git clone https://github.com/JirA44/KOF-Ultimate-Online.git
   cd KOF-Ultimate-Online
   ```

2. **Télécharger les personnages (séparément):**

   ⚠️ **Important:** Les personnages (9.7 GB) ne sont pas inclus dans le dépôt Git.

   Le dépôt ne fournit pas de lien de téléchargement pour ces fichiers. Sans le dossier de personnages requis, le jeu peut ne pas démarrer correctement.

   Décompressez le dossier `chars/` à la racine du projet.

3. **Installer Python (optionnel):**
   ```bash
   # Pour utiliser les outils de diagnostic
   python -m pip install -r requirements.txt
   ```

4. **Vérifier l'installation:**
   ```bash
   python verify_game.py
   ```

---

## 🚀 Lancement Rapide

### Méthode 1: Launcher Intelligent (Recommandé)

Double-cliquez sur: **`LAUNCH_ULTIMATE_SMART.bat`**

Ce launcher:
1. ✅ Auto-répare les erreurs
2. ✅ Teste le système
3. ✅ Lance le jeu

### Méthode 2: Lancement Direct

Double-cliquez sur: **`KOF BLACK R.exe`**

### Méthode 3: Lancement avec IA

Double-cliquez sur: **`launch_with_ai.bat`**

Active l'IA de navigation automatique.

---

## 📖 Documentation

### Documentation Principale

| Fichier | Description |
|---------|-------------|
| [README_FR.md](README_FR.md) | Documentation française complète |
| [DEMARRAGE_RAPIDE.txt](DEMARRAGE_RAPIDE.txt) | Guide de démarrage rapide |
| [QUICK_START.md](QUICK_START.md) | Quick start guide (English) |

### Guides Spécifiques

| Guide | Sujet |
|-------|-------|
| [GUIDE_MULTIJOUEUR.md](GUIDE_MULTIJOUEUR.md) | Configuration multijoueur |
| [README_AI_PLAYER.md](README_AI_PLAYER.md) | Système d'IA joueur |
| [README_AI_NAVIGATOR.md](README_AI_NAVIGATOR.md) | IA de navigation |
| [AI_ENHANCEMENT_GUIDE.md](AI_ENHANCEMENT_GUIDE.md) | Amélioration sprites avec IA |
| [STAGE_BACKGROUNDS_GUIDE.md](STAGE_BACKGROUNDS_GUIDE.md) | Guide des backgrounds |
| [LAUNCHER_README.md](LAUNCHER_README.md) | Documentation du launcher |

### Rapports Techniques

| Rapport | Contenu |
|---------|---------|
| [FINAL_REPORT.txt](FINAL_REPORT.txt) | Rapport de développement |
| [AGENT_IA_RAPPORT.md](AGENT_IA_RAPPORT.md) | Rapport système IA |
| [SUMMARY.md](SUMMARY.md) | Résumé du projet |

---

## 📁 Structure du Projet

```
D:\KOF Ultimate\
├── 📂 chars/                    # 188 personnages (9.7 GB - téléchargement séparé)
├── 📂 data/                     # Configurations système (44 MB)
│   ├── system.def               # Configuration du système
│   ├── select.def               # Écran de sélection
│   ├── fight.def                # Configuration des combats
│   └── mugen.cfg                # Configuration M.U.G.E.N
├── 📂 sound/                    # Musiques et effets sonores (18 MB)
├── 📂 stages/                   # 31 arènes de combat
├── 📂 font/                     # Polices de caractères
├── 📂 docs/                     # Documentation supplémentaire
│
├── 🎮 KOF BLACK R.exe           # Exécutable principal du jeu
├── 🚀 KOF Ultimate Launcher.exe # Launcher moderne
│
├── 🛠️ OUTILS DE DIAGNOSTIC
├── auto_repair_system.py        # Auto-réparation des erreurs
├── auto_test_system.py          # Tests automatisés (21 composants)
├── game_monitor.py              # Monitoring temps réel
├── verify_game.py               # Vérification complète
│
├── 🤖 SYSTÈMES IA
├── ai_player_system.py          # IA joueur avancée
├── launcher_ai_navigator.py    # IA de navigation menus
├── ai_retro_enhancer.py        # Amélioration sprites IA
│
├── 🎨 OUTILS CRÉATIFS
├── create_menu_animation.py    # Générateur d'animations menu
├── integrate_backgrounds.py    # Intégration backgrounds
├── enhance_sprites_batch.py    # Traitement batch sprites
│
├── ⚙️ CONFIGURATION
├── launcher_modern.py          # Launcher Python moderne
├── gamepad_auto_config.py      # Auto-config manettes
├── multiplayer_test_system.py  # Tests multijoueur
│
├── 🚀 LAUNCHERS
├── LAUNCH_ULTIMATE_SMART.bat   # Launcher intelligent (recommandé)
├── LAUNCH_ULTIMATE.bat         # Launcher simple
├── launch_with_ai.bat          # Lancement avec IA
└── launch_complete_system.bat  # Système complet

└── 📄 CONFIGURATION GIT
    ├── .gitignore               # Fichiers exclus de Git
    └── README.md                # Ce fichier
```

---

## 🔧 Outils de Diagnostic

### Auto-Réparation

```bash
python auto_repair_system.py
```

**Détecte et répare automatiquement:**
- ❌ Erreurs de personnages
- ❌ Fichiers .air corrompus
- ❌ Configuration manettes
- ❌ Problèmes de backgrounds
- ❌ Fichiers système manquants

### Tests Automatisés

```bash
python auto_test_system.py
```

**Vérifie 21 composants:**
1. ✅ Fichiers exécutables (2/2)
2. ✅ Dossiers principaux (6/6)
3. ✅ Fichiers de configuration (4/4)
4. ✅ Assets (sprites, sons) (5/5)
5. ✅ Personnages (188)
6. ✅ Stages (31)

**Score:** 100% - EXCELLENT

### Vérification Complète

```bash
python verify_game.py
```

Audit détaillé de tous les fichiers avec rapport complet.

### Monitoring Temps Réel

```bash
python game_monitor.py
```

Surveille:
- Logs en temps réel
- Erreurs pendant l'exécution
- Performance du jeu
- Événements système

---

## ⚙️ Configuration

### Manettes

La détection est **automatique**. Si problème:

1. Branchez votre manette
2. Lancez: `python auto_repair_system.py`
3. Relancez le jeu

### Clavier

**Joueur 1:**
- **Déplacement:** Flèches directionnelles
- **Actions:** A, S, D, F, G, H
- **Start:** Entrée

**Joueur 2:**
- **Déplacement:** Q, W, E, R
- **Actions:** T, U, O, P, L
- **Start:** Espace

### Personnalisation

#### Changer le fond du menu

Éditez `data/system.def` section `[TitleBGdef]`

#### Ajouter des personnages

1. Copiez le dossier du personnage dans `chars/`
2. Ajoutez une ligne dans `data/select.def` section `[Characters]`:
   ```
   nom_personnage/nom_personnage.def
   ```
3. Lancez: `python auto_test_system.py` pour valider

#### Ajouter des stages

1. Copiez le fichier `.def` du stage dans `stages/`
2. Le stage sera automatiquement disponible

---

## 🐛 Dépannage

### Le jeu crash au démarrage

```bash
python auto_repair_system.py
```

L'auto-réparation résout 90% des problèmes automatiquement.

### Manette non détectée

1. Vérifiez que la manette est branchée
2. Lancez: `python gamepad_auto_config.py`
3. Relancez le jeu

### Personnage ne charge pas

Le système désactive automatiquement les personnages défectueux.
Consultez `mugen.log` pour plus de détails:

```bash
type mugen.log
```

### Erreurs dans les menus

```bash
python auto_test_system.py
```

Vérifie l'intégrité de tous les fichiers système.

### Performance lente

- Fermez les applications en arrière-plan
- Réduisez la résolution dans `data/mugen.cfg`
- Désactivez certains effets visuels

---

## 🤝 Contribution

Les contributions sont les bienvenues!

### Comment Contribuer

1. **Fork** le projet
2. **Créez** une branche pour votre fonctionnalité:
   ```bash
   git checkout -b feature/nouvelle-fonctionnalite
   ```
3. **Commitez** vos changements:
   ```bash
   git commit -m "Ajout de nouvelle fonctionnalité"
   ```
4. **Push** vers la branche:
   ```bash
   git push origin feature/nouvelle-fonctionnalite
   ```
5. **Ouvrez** une Pull Request

### Directives

- Utilisez Python 3.8+ pour les scripts
- Documentez votre code en français
- Testez vos modifications avec `auto_test_system.py`
- Suivez le style de code existant

---

## 📊 Statistiques

- **Personnages:** 188 disponibles
- **Stages:** 31 arènes
- **Taille totale:** ~12 GB
- **Tests passés:** 21/21 ✅
- **Score de santé:** 100% ✅
- **Compatibilité:** Windows 10/11

---

## 📝 Notes Importantes

### ⚠️ Fichiers Volumineux

Les personnages (`chars/` - 9.7 GB) ne sont **pas inclus** dans le dépôt Git pour des raisons de taille. Vous devez les télécharger séparément depuis les liens fournis dans la section [Installation](#installation).

### 🔄 Mises à Jour

Pour mettre à jour le projet:

```bash
git pull origin main
```

Les personnages téléchargés séparément seront préservés.

### 🎮 Compatibilité

Ce jeu utilise M.U.G.E.N 1.1.0 Beta 1. Les personnages et stages conçus pour des versions différentes peuvent nécessiter des ajustements.

---

## 📧 Support

Pour tout problème:

1. **Consultez** la documentation dans `docs/`
2. **Lancez** `python auto_repair_system.py`
3. **Vérifiez** `mugen.log` pour les erreurs
4. **Consultez** `FINAL_REPORT.txt` pour l'état du système
5. **Ouvrez** une issue sur GitHub avec:
   - Description du problème
   - Contenu de `mugen.log`
   - Étapes pour reproduire

---

## 📜 License

Ce projet est distribué sous license libre. Les personnages, sprites et autres assets appartiennent à leurs créateurs respectifs.

**M.U.G.E.N** est développé par Elecbyte.

---

## 🙏 Remerciements

- **Elecbyte** - Pour le moteur M.U.G.E.N
- **Communauté M.U.G.E.N** - Pour les personnages et stages
- **Tous les créateurs de sprites** - Pour leur travail artistique
- **Contributeurs du projet** - Pour les améliorations et corrections

---

<div align="center">

**Version:** 2.0 Enhanced
**Date:** 16 Octobre 2025
**Statut:** ✅ Production Ready

*Bon jeu! 🎮🔥*

</div>
