# 🎮 WORKFLOW COMPLET - De 2/20 à 18+/20

## 📋 Système de Tests et Nettoyage Automatiques

### Phase 1: Détection des Bugs 🔍

**Fichier: AI_TESTERS_ADVANCED.py**

Lance **4 testeurs IA en parallèle** avec des profils différents:

#### 🤖 Profils de Testeurs

1. **CRASHER** 💥
   - Focus: Crashs au démarrage, chargement, sélection
   - Stratégie: Redémarrages rapides répétés
   - Détecte: Bugs de startup critiques

2. **EXPLORER** 🗺️
   - Focus: Tous personnages, tous stages
   - Stratégie: Couverture exhaustive
   - Détecte: Personnages/stages cassés

3. **STRESS_TESTER** ⚡
   - Focus: Bugs de gameplay
   - Stratégie: Spam d'inputs intensifs
   - Détecte: Bugs d'animation, collision, gameplay

4. **RAGE_QUITTER** 🚪
   - Focus: Exits rapides, interruptions
   - Stratégie: Tests de cleanup et état
   - Détecte: Memory leaks, bugs de sortie

#### 📊 Résultats

Les testeurs génèrent automatiquement:

- **BUG_DATABASE.json**: Base de données complète de tous les bugs
- **BUG_REPORT_[date].md**: Rapports lisibles générés tous les 10 tests
- **ai_testers.log**: Logs en temps réel

La base de données catégorise:
- ❌ **Personnages cassés** (à retirer)
- 🗺️ **Stages cassés** (à retirer)
- 💥 **Crashs** (avec stack traces)
- 🎮 **Bugs de gameplay**
- 🎨 **Bugs visuels**
- 🐌 **Problèmes de performance**

### Phase 2: Nettoyage Automatique 🧹

**Fichier: AUTO_CLEAN_BROKEN_CONTENT.py**

Une fois les bugs détectés, ce script:

1. ✅ Lit la BUG_DATABASE.json
2. 💾 Crée un backup complet (BACKUP_[date]/)
3. 🗑️ Supprime les personnages cassés de chars/
4. 🗑️ Supprime les stages cassés de stages/
5. ✏️ Met à jour data/select.def (commente les lignes cassées)
6. 📄 Génère un rapport de nettoyage

**Sécurité:**
- Demande confirmation avant suppression
- Backup automatique de tout
- Possibilité de restauration facile

### Phase 3: Validation 🎯

Après nettoyage:

1. 🎮 Relancer le jeu manuellement
2. 🤖 Relancer AI_TESTERS_ADVANCED.py
3. 📊 Vérifier amélioration du score qualité
4. 🔄 Répéter jusqu'à atteindre 18+/20

---

## 🚀 Comment Utiliser

### 1. Lancer les Testeurs IA

```batch
# Option A: Via launcher batch
LAUNCH_AI_TESTERS.bat

# Option B: Direct Python
python AI_TESTERS_ADVANCED.py
```

Les testeurs tourneront **EN PERMANENCE** et détecteront tous les bugs.

**Laisser tourner plusieurs heures** pour une détection complète!

### 2. Consulter les Résultats

Pendant que les tests tournent:

```batch
# Voir les logs en direct
type ai_testers.log

# Consulter la base de bugs
notepad BUG_DATABASE.json

# Lire le dernier rapport
# Ouvrir le dernier fichier BUG_REPORT_*.md
```

### 3. Nettoyer le Contenu Cassé

Une fois assez de tests effectués (minimum 50-100):

```batch
python AUTO_CLEAN_BROKEN_CONTENT.py
```

Le script vous montrera ce qui sera supprimé et demandera confirmation.

### 4. Valider les Corrections

Après nettoyage:

```batch
# Relancer les testeurs
python AI_TESTERS_ADVANCED.py
```

Vérifier que:
- ✅ Moins de crashs détectés
- ✅ Score qualité augmente
- ✅ Bugs critiques résolus

---

## 📊 Critères de Qualité Esport

### Score /20 Calculé Automatiquement

**Pénalités:**
- Bugs critiques: **-5 points** chacun
- Bugs majeurs: **-2 points** chacun
- Bugs mineurs: **-0.5 point** chacun
- Bugs visuels: **-0.2 point** chacun

### Objectifs par Score

- **2-5/20**: 🔴 État actuel - Nombreux crashs
- **5-10/20**: 🟠 Instable - Bugs critiques restants
- **10-15/20**: 🟡 Jouable - Corrections importantes
- **15-18/20**: 🟢 Bonne qualité - Presque prêt
- **18-20/20**: 🏆 **ESPORT READY!**

---

## 🐛 Types de Bugs Détectés

### 🔴 Critiques (Bloquants Esport)

- 💥 Crash au démarrage
- 💥 Crash sélection personnage
- 💥 Crash chargement combat
- 💥 Crash pendant combat
- 🚫 Personnage totalement injouable
- 🗺️ Stage qui fait planter
- 🌐 Système multijoueur cassé

### 🟠 Majeurs (Impact Qualité)

- 🐌 Memory leaks
- ⏱️ Timeouts (matchs trop longs)
- 🎨 Portraits manquants
- 🖼️ Icônes désynchronisées
- 🎮 Bugs de gameplay sévères
- 📊 Problèmes de performance

### 🟡 Mineurs

- 🎨 Petits bugs visuels
- 🔊 Problèmes audio
- ⌨️ Bugs d'input légers

---

## 📁 Fichiers Générés

```
D:\KOF Ultimate Online\
├── AI_TESTERS_ADVANCED.py          # Système de testeurs IA
├── AUTO_CLEAN_BROKEN_CONTENT.py    # Nettoyeur automatique
├── LAUNCH_AI_TESTERS.bat           # Launcher Windows
├── BUG_DATABASE.json               # Base de données bugs
├── ai_testers.log                  # Logs temps réel
├── BUG_REPORTS\                    # Dossier rapports
│   ├── BUG_REPORT_20241106_120000.md
│   └── BUG_REPORT_20241106_130000.md
├── BACKUP_20241106_120000\         # Backups automatiques
│   ├── chars\
│   ├── stages\
│   └── data\
└── CLEANUP_REPORT_20241106.md      # Rapports nettoyage
```

---

## ⚙️ Configuration

### Personnaliser les Testeurs

Éditer `AI_TESTERS_ADVANCED.py`:

```python
# Ligne 552: Choisir les profils à lancer
profiles_to_run = [
    "CRASHER",
    "EXPLORER",
    "STRESS_TESTER",
    "RAGE_QUITTER",
    # "VISUAL_INSPECTOR",  # Décommenter pour activer
    # "LONG_RUNNER",       # Tests longs (memory leaks)
    # "MENU_NAVIGATOR",    # Tests UI
    # "RANDOM_CHAOS",      # Tests chaotiques
]
```

### Ajuster la Durée des Tests

```python
# Durée de chaque combat (secondes)
combat_duration = 10  # Défaut: 10s

# Pause entre tests
pause_between_tests = 2  # Défaut: 2s
```

---

## 🔧 Dépannage

### Les testeurs ne démarrent pas

```batch
# Vérifier Python
python --version

# Installer dépendances
pip install psutil pyautogui

# Vérifier les fichiers
dir AI_TESTERS_ADVANCED.py
```

### Aucun bug détecté

- ✅ Laisser tourner plus longtemps (minimum 1h)
- ✅ Vérifier que le jeu se lance correctement
- ✅ Consulter ai_testers.log pour erreurs

### Le jeu crash trop souvent

C'est normal! C'est exactement ce que les testeurs doivent détecter.
Après 50-100 tests, lancez le nettoyeur pour retirer le contenu cassé.

---

## 🎯 Roadmap vers 18+/20

### Itération 1: Détection Initiale
- [ ] Lancer AI_TESTERS_ADVANCED.py
- [ ] Laisser tourner 2-3 heures
- [ ] Obtenir premier rapport complet

### Itération 2: Premier Nettoyage
- [ ] Exécuter AUTO_CLEAN_BROKEN_CONTENT.py
- [ ] Valider suppressions
- [ ] Tester manuellement le jeu

### Itération 3: Validation
- [ ] Relancer testeurs IA
- [ ] Vérifier amélioration score
- [ ] Corriger bugs restants

### Itération 4: Polish Final
- [ ] Tests longs (LONG_RUNNER profile)
- [ ] Tests visuels (VISUAL_INSPECTOR)
- [ ] Validation finale

**Objectif: 18+/20** 🏆

---

## 📞 Support

Tous les rapports sont générés automatiquement.

En cas de problème:
1. Consulter ai_testers.log
2. Vérifier BUG_DATABASE.json
3. Lire les rapports markdown générés

---

*Système créé pour atteindre la qualité esport*
*De 2/20 à 18+/20 via tests automatisés* 🎮
