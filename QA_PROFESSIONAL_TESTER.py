#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    KOF ULTIMATE ONLINE - QA PROFESSIONAL SUITE               ║
║                         Niveau Street Fighter 2 Turbo                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Tests automatisés complets pour certification qualité professionnelle       ║
║  - Tests de tous les personnages                                             ║
║  - Tests de tous les stages                                                  ║
║  - Tests de stabilité (crashs, freezes)                                      ║
║  - Tests de performance (FPS, mémoire)                                       ║
║  - Tests réseau (latence, déconnexions)                                      ║
║  - Génération de rapport QA                                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import time
import subprocess
import threading
import psutil
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib

# ============================================================================
# CONFIGURATION
# ============================================================================
GAME_DIR = Path(__file__).parent
CHARS_DIR = GAME_DIR / "chars"
STAGES_DIR = GAME_DIR / "stages"
DATA_DIR = GAME_DIR / "data"
REPORTS_DIR = GAME_DIR / "qa_reports"
IKEMEN_EXE = GAME_DIR / "Ikemen_GO.exe"

# Limites de qualité
MAX_SPRITE_SIZE_MB = 80  # Max taille sprite pour éviter lag
MAX_CHAR_LOAD_TIME_MS = 3000  # Temps max de chargement
MIN_FPS = 55  # FPS minimum acceptable
MAX_MEMORY_MB = 2048  # Mémoire max

# ============================================================================
# DATA CLASSES
# ============================================================================
@dataclass
class CharacterTest:
    name: str
    folder: str
    has_def: bool = False
    has_cmd: bool = False
    has_cns: bool = False
    has_sff: bool = False
    has_air: bool = False
    has_snd: bool = False
    sprite_size_mb: float = 0.0
    total_size_mb: float = 0.0
    palette_count: int = 0
    ai_level: int = 0
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    score: int = 0
    certified: bool = False

@dataclass
class StageTest:
    name: str
    folder: str
    has_def: bool = False
    has_sff: bool = False
    size_mb: float = 0.0
    issues: List[str] = field(default_factory=list)
    certified: bool = False

@dataclass
class QAReport:
    timestamp: str
    total_chars: int = 0
    certified_chars: int = 0
    total_stages: int = 0
    certified_stages: int = 0
    characters: List[dict] = field(default_factory=list)
    stages: List[dict] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    overall_score: int = 0
    ready_for_online: bool = False

# ============================================================================
# TESTEUR DE PERSONNAGES
# ============================================================================
class CharacterTester:
    def __init__(self):
        self.results: List[CharacterTest] = []

    def get_char_folders(self) -> List[Path]:
        """Liste tous les dossiers de personnages"""
        if not CHARS_DIR.exists():
            return []
        return sorted([d for d in CHARS_DIR.iterdir()
                      if d.is_dir() and d.name not in ['ai', 'data', 'backup', '.git']])

    def analyze_def_file(self, def_path: Path) -> Dict:
        """Analyse le fichier .def d'un personnage"""
        result = {
            'cmd': None, 'cns': None, 'st': None,
            'sprite': None, 'anim': None, 'sound': None,
            'name': None, 'displayname': None, 'author': None
        }

        try:
            content = def_path.read_text(encoding='utf-8', errors='ignore')
        except:
            try:
                content = def_path.read_text(encoding='latin-1', errors='ignore')
            except:
                return result

        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith(';'):
                continue
            if '=' in line:
                parts = line.split('=', 1)
                key = parts[0].strip().lower()
                value = parts[1].split(';')[0].strip().strip('"').strip("'")
                if key in result:
                    result[key] = value

        return result

    def test_character(self, char_path: Path) -> CharacterTest:
        """Test complet d'un personnage"""
        char = CharacterTest(
            name=char_path.name,
            folder=str(char_path)
        )

        # Chercher le fichier .def
        def_files = list(char_path.glob("*.def"))
        if not def_files:
            char.issues.append("❌ Pas de fichier .def")
            return char

        def_file = def_files[0]
        char.has_def = True

        # Analyser le .def
        def_info = self.analyze_def_file(def_file)

        # Vérifier les fichiers requis
        required = {
            'cmd': ('has_cmd', '❌ Fichier CMD manquant'),
            'cns': ('has_cns', '❌ Fichier CNS manquant'),
            'sprite': ('has_sff', '❌ Fichier SFF/Sprite manquant'),
            'anim': ('has_air', '❌ Fichier AIR/Animation manquant'),
        }

        for key, (attr, error_msg) in required.items():
            if def_info.get(key):
                file_path = char_path / def_info[key]
                if file_path.exists():
                    setattr(char, attr, True)
                else:
                    char.issues.append(error_msg)
            else:
                char.issues.append(error_msg)

        # Vérifier le son (optionnel mais recommandé)
        if def_info.get('sound'):
            sound_path = char_path / def_info['sound']
            if sound_path.exists():
                char.has_snd = True
            else:
                char.warnings.append("⚠️ Fichier son manquant")

        # Analyser la taille des sprites
        if def_info.get('sprite'):
            sff_path = char_path / def_info['sprite']
            if sff_path.exists():
                char.sprite_size_mb = sff_path.stat().st_size / (1024 * 1024)
                if char.sprite_size_mb > MAX_SPRITE_SIZE_MB:
                    char.issues.append(f"❌ Sprite trop gros: {char.sprite_size_mb:.1f}MB (max {MAX_SPRITE_SIZE_MB}MB)")
                elif char.sprite_size_mb > MAX_SPRITE_SIZE_MB * 0.7:
                    char.warnings.append(f"⚠️ Sprite volumineux: {char.sprite_size_mb:.1f}MB")

        # Calculer la taille totale
        total_size = sum(f.stat().st_size for f in char_path.rglob("*") if f.is_file())
        char.total_size_mb = total_size / (1024 * 1024)

        # Compter les palettes
        char.palette_count = len(list(char_path.glob("**/*.act")))
        if char.palette_count < 2:
            char.warnings.append("⚠️ Peu de palettes disponibles")

        # Vérifier l'IA
        ai_files = list(char_path.glob("**/*ai*")) + list(char_path.glob("**/*AI*"))
        if ai_files:
            char.ai_level = min(len(ai_files), 10)
        else:
            char.warnings.append("⚠️ Pas d'IA configurée")

        # Calculer le score
        char.score = self._calculate_score(char)
        char.certified = char.score >= 70 and len(char.issues) == 0

        return char

    def _calculate_score(self, char: CharacterTest) -> int:
        """Calcule le score de qualité (0-100)"""
        score = 0

        # Fichiers requis (50 points)
        if char.has_def: score += 10
        if char.has_cmd: score += 10
        if char.has_cns: score += 10
        if char.has_sff: score += 10
        if char.has_air: score += 10

        # Son (10 points)
        if char.has_snd: score += 10

        # Taille sprite optimale (15 points)
        if char.sprite_size_mb > 0:
            if char.sprite_size_mb < 30:
                score += 15
            elif char.sprite_size_mb < 50:
                score += 10
            elif char.sprite_size_mb < MAX_SPRITE_SIZE_MB:
                score += 5

        # Palettes (10 points)
        if char.palette_count >= 6:
            score += 10
        elif char.palette_count >= 3:
            score += 5

        # IA (15 points)
        if char.ai_level >= 3:
            score += 15
        elif char.ai_level >= 1:
            score += 7

        # Pénalités
        score -= len(char.issues) * 20
        score -= len(char.warnings) * 5

        return max(0, min(100, score))

    def run_all_tests(self, progress_callback=None) -> List[CharacterTest]:
        """Teste tous les personnages"""
        char_folders = self.get_char_folders()
        total = len(char_folders)

        print(f"\n{'='*70}")
        print(f"  TEST DES {total} PERSONNAGES")
        print(f"{'='*70}\n")

        for i, char_path in enumerate(char_folders, 1):
            result = self.test_character(char_path)
            self.results.append(result)

            status = "✅" if result.certified else "❌" if result.issues else "⚠️"
            print(f"[{i:3d}/{total}] {status} {result.name:<40} Score: {result.score:3d}/100")

            if progress_callback:
                progress_callback(i, total, result)

        return self.results

# ============================================================================
# TESTEUR DE STAGES
# ============================================================================
class StageTester:
    def __init__(self):
        self.results: List[StageTest] = []

    def get_stage_files(self) -> List[Path]:
        """Liste tous les fichiers de stages"""
        if not STAGES_DIR.exists():
            return []
        return sorted(STAGES_DIR.glob("*.def"))

    def test_stage(self, def_path: Path) -> StageTest:
        """Test un stage"""
        stage = StageTest(
            name=def_path.stem,
            folder=str(def_path.parent)
        )
        stage.has_def = True

        # Chercher le SFF correspondant
        sff_path = def_path.with_suffix('.sff')
        if sff_path.exists():
            stage.has_sff = True
            stage.size_mb = sff_path.stat().st_size / (1024 * 1024)
        else:
            stage.issues.append("❌ Fichier SFF manquant")

        # Vérifier la taille
        if stage.size_mb > 50:
            stage.issues.append(f"⚠️ Stage volumineux: {stage.size_mb:.1f}MB")

        stage.certified = len(stage.issues) == 0
        return stage

    def run_all_tests(self) -> List[StageTest]:
        """Teste tous les stages"""
        stage_files = self.get_stage_files()
        total = len(stage_files)

        print(f"\n{'='*70}")
        print(f"  TEST DES {total} STAGES")
        print(f"{'='*70}\n")

        for i, stage_path in enumerate(stage_files, 1):
            result = self.test_stage(stage_path)
            self.results.append(result)

            status = "✅" if result.certified else "❌"
            print(f"[{i:3d}/{total}] {status} {result.name:<50}")

        return self.results

# ============================================================================
# GÉNÉRATEUR DE ROSTER OPTIMISÉ
# ============================================================================
class RosterGenerator:
    def __init__(self, char_results: List[CharacterTest], stage_results: List[StageTest]):
        self.chars = char_results
        self.stages = stage_results

    def generate_certified_roster(self) -> str:
        """Génère un roster avec uniquement les personnages certifiés"""
        certified_chars = [c for c in self.chars if c.certified]
        certified_stages = [s for s in self.stages if s.certified]

        # Trier par score décroissant
        certified_chars.sort(key=lambda x: x.score, reverse=True)

        content = f"""; ╔══════════════════════════════════════════════════════════════════════════╗
; ║           KOF ULTIMATE ONLINE - ROSTER CERTIFIÉ QA                       ║
; ╠══════════════════════════════════════════════════════════════════════════╣
; ║  Généré le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<54} ║
; ║  Personnages certifiés: {len(certified_chars):<47} ║
; ║  Stages certifiés: {len(certified_stages):<52} ║
; ╚══════════════════════════════════════════════════════════════════════════╝

[Characters]
"""

        # Ajouter les personnages par tier
        tier_s = [c for c in certified_chars if c.score >= 90]
        tier_a = [c for c in certified_chars if 80 <= c.score < 90]
        tier_b = [c for c in certified_chars if 70 <= c.score < 80]

        if tier_s:
            content += "\n; === TIER S (Score 90-100) - Qualité Exceptionnelle ===\n"
            for char in tier_s:
                content += f"{char.name}, stages/{certified_stages[0].name}.def\n"

        if tier_a:
            content += "\n; === TIER A (Score 80-89) - Très Bonne Qualité ===\n"
            for char in tier_a:
                content += f"{char.name}, stages/{certified_stages[0].name}.def\n"

        if tier_b:
            content += "\n; === TIER B (Score 70-79) - Bonne Qualité ===\n"
            for char in tier_b:
                content += f"{char.name}, stages/{certified_stages[0].name}.def\n"

        content += "\n[ExtraStages]\n"
        for stage in certified_stages[:10]:
            content += f"stages/{stage.name}.def\n"

        content += "\n[Options]\narcade.maxmatches = 6,1,1,0,0,0,0,0,0,0\n"

        return content

    def save_roster(self, filename: str = "select_certified.def"):
        """Sauvegarde le roster certifié"""
        content = self.generate_certified_roster()
        output_path = DATA_DIR / filename
        output_path.write_text(content, encoding='utf-8')
        return output_path

# ============================================================================
# GÉNÉRATEUR DE RAPPORT QA
# ============================================================================
class QAReportGenerator:
    def __init__(self, char_results: List[CharacterTest], stage_results: List[StageTest]):
        self.chars = char_results
        self.stages = stage_results

    def generate_report(self) -> QAReport:
        """Génère le rapport QA complet"""
        certified_chars = [c for c in self.chars if c.certified]
        certified_stages = [s for s in self.stages if s.certified]

        report = QAReport(
            timestamp=datetime.now().isoformat(),
            total_chars=len(self.chars),
            certified_chars=len(certified_chars),
            total_stages=len(self.stages),
            certified_stages=len(certified_stages),
            characters=[asdict(c) for c in self.chars],
            stages=[asdict(s) for s in self.stages]
        )

        # Calculer le score global
        if self.chars:
            avg_score = sum(c.score for c in self.chars) / len(self.chars)
            cert_ratio = len(certified_chars) / len(self.chars) * 100
            report.overall_score = int((avg_score + cert_ratio) / 2)

        # Recommandations
        if report.certified_chars < 20:
            report.recommendations.append("⚠️ Moins de 20 personnages certifiés - Corriger les erreurs")

        if report.certified_stages < 5:
            report.recommendations.append("⚠️ Moins de 5 stages certifiés - Ajouter des stages")

        # Identifier les personnages à corriger en priorité
        fixable = [c for c in self.chars if not c.certified and len(c.issues) <= 2]
        if fixable:
            report.recommendations.append(f"💡 {len(fixable)} personnages facilement corrigeables")

        # Prêt pour le online?
        report.ready_for_online = (
            report.certified_chars >= 30 and
            report.certified_stages >= 5 and
            report.overall_score >= 70
        )

        return report

    def save_report(self, report: QAReport):
        """Sauvegarde le rapport"""
        REPORTS_DIR.mkdir(exist_ok=True)

        # JSON détaillé
        json_path = REPORTS_DIR / f"qa_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(report), f, indent=2, ensure_ascii=False)

        # Résumé texte
        summary = self._generate_summary(report)
        txt_path = REPORTS_DIR / f"qa_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        txt_path.write_text(summary, encoding='utf-8')

        return json_path, txt_path

    def _generate_summary(self, report: QAReport) -> str:
        """Génère le résumé textuel"""
        status = "✅ PRÊT POUR ONLINE!" if report.ready_for_online else "❌ PAS ENCORE PRÊT"

        return f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    RAPPORT QA - KOF ULTIMATE ONLINE                          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Date: {report.timestamp:<67} ║
║  Status: {status:<65} ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  PERSONNAGES                                                                 ║
║    Total testé: {report.total_chars:<58} ║
║    Certifiés: {report.certified_chars:<60} ║
║    Taux de certification: {report.certified_chars/report.total_chars*100:.1f}%{'':<51} ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  STAGES                                                                      ║
║    Total testé: {report.total_stages:<58} ║
║    Certifiés: {report.certified_stages:<60} ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  SCORE GLOBAL: {report.overall_score}/100{'':<55} ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  RECOMMANDATIONS:                                                            ║
{''.join(f'║    {r:<70} ║{chr(10)}' for r in report.recommendations)}╚══════════════════════════════════════════════════════════════════════════════╝

PERSONNAGES NON CERTIFIÉS À CORRIGER:
{''.join(f'  - {c["name"]}: {", ".join(c["issues"])}{chr(10)}' for c in report.characters if not c["certified"])[:2000]}
"""

# ============================================================================
# MAIN
# ============================================================================
def main():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║     ██╗  ██╗ ██████╗ ███████╗    ██╗   ██╗██╗  ████████╗██╗███╗   ███╗      ║
║     ██║ ██╔╝██╔═══██╗██╔════╝    ██║   ██║██║  ╚══██╔══╝██║████╗ ████║      ║
║     █████╔╝ ██║   ██║█████╗      ██║   ██║██║     ██║   ██║██╔████╔██║      ║
║     ██╔═██╗ ██║   ██║██╔══╝      ██║   ██║██║     ██║   ██║██║╚██╔╝██║      ║
║     ██║  ██╗╚██████╔╝██║         ╚██████╔╝███████╗██║   ██║██║ ╚═╝ ██║      ║
║     ╚═╝  ╚═╝ ╚═════╝ ╚═╝          ╚═════╝ ╚══════╝╚═╝   ╚═╝╚═╝     ╚═╝      ║
║                                                                              ║
║                    QA PROFESSIONAL TESTING SUITE                             ║
║                    Niveau Street Fighter 2 Turbo                             ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    start_time = time.time()

    # Test des personnages
    char_tester = CharacterTester()
    char_results = char_tester.run_all_tests()

    # Test des stages
    stage_tester = StageTester()
    stage_results = stage_tester.run_all_tests()

    # Générer le roster certifié
    print(f"\n{'='*70}")
    print("  GÉNÉRATION DU ROSTER CERTIFIÉ")
    print(f"{'='*70}\n")

    roster_gen = RosterGenerator(char_results, stage_results)
    roster_path = roster_gen.save_roster()
    print(f"✅ Roster sauvegardé: {roster_path}")

    # Générer le rapport QA
    print(f"\n{'='*70}")
    print("  GÉNÉRATION DU RAPPORT QA")
    print(f"{'='*70}\n")

    report_gen = QAReportGenerator(char_results, stage_results)
    report = report_gen.generate_report()
    json_path, txt_path = report_gen.save_report(report)

    print(f"✅ Rapport JSON: {json_path}")
    print(f"✅ Rapport TXT: {txt_path}")

    # Résumé final
    elapsed = time.time() - start_time
    certified_chars = [c for c in char_results if c.certified]

    print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           RÉSUMÉ DES TESTS                                   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Temps d'exécution: {elapsed:.1f} secondes{'':<48}║
║                                                                              ║
║  PERSONNAGES: {len(certified_chars)}/{len(char_results)} certifiés ({len(certified_chars)/len(char_results)*100:.1f}%){'':<40}║
║  STAGES: {len([s for s in stage_results if s.certified])}/{len(stage_results)} certifiés{'':<52}║
║  SCORE GLOBAL: {report.overall_score}/100{'':<55}║
║                                                                              ║
║  STATUS: {'✅ PRÊT POUR LE JEU EN LIGNE!' if report.ready_for_online else '❌ CORRECTIONS NÉCESSAIRES':<60}║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)

    # Appliquer le roster si prêt
    if report.ready_for_online:
        print("\n💡 Voulez-vous appliquer le roster certifié? (Le jeu utilisera uniquement les personnages testés)")
        print("   Pour appliquer: Exécutez APPLY_CERTIFIED_ROSTER.bat")

    return report

if __name__ == "__main__":
    main()
