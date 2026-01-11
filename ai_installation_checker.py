"""
KOF Ultimate - IA Vérificateur d'Installation All-in-One
Vérifie que toute l'installation est complète et ne manque de rien
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

class InstallationChecker:
    """IA qui vérifie l'intégralité de l'installation"""

    def __init__(self):
        self.base_path = Path("D:/KOF Ultimate Online kofuo")
        self.problems = []
        self.warnings = []
        self.checks_passed = []

    def log(self, message, level="INFO"):
        """Log avec couleur"""
        colors = {
            "INFO": "",
            "SUCCESS": "✓ ",
            "WARNING": "⚠️  ",
            "ERROR": "❌ "
        }
        prefix = colors.get(level, "")
        print(f"{prefix}{message}")

    def check_essential_files(self):
        """Vérifie les fichiers essentiels"""
        self.log("\n📁 Vérification des fichiers essentiels...", "INFO")

        essential = [
            ("KOF_Ultimate_Online.exe", "Exécutable principal du jeu"),
            ("data/mugen.cfg", "Configuration MUGEN"),
            ("data/system.def", "Définition du système"),
            ("data/system.sff", "Sprites du système"),
            ("data/system.snd", "Sons du système"),
            ("data/select.def", "Liste des personnages"),
            ("data/fight.def", "Configuration des combats"),
        ]

        for file_path, description in essential:
            full_path = self.base_path / file_path
            if full_path.exists():
                self.log(f"  {description}: OK", "SUCCESS")
                self.checks_passed.append(file_path)
            else:
                self.log(f"  {description}: MANQUANT", "ERROR")
                self.problems.append(f"Missing: {file_path} - {description}")

    def check_directories(self):
        """Vérifie les dossiers requis"""
        self.log("\n📂 Vérification des dossiers...", "INFO")

        required_dirs = [
            ("chars", "Personnages"),
            ("stages", "Arènes/Stages"),
            ("data", "Données du jeu"),
            ("font", "Polices"),
            ("sound", "Sons"),
        ]

        for dir_name, description in required_dirs:
            dir_path = self.base_path / dir_name
            if dir_path.exists() and dir_path.is_dir():
                # Compter les fichiers
                file_count = len(list(dir_path.iterdir()))
                self.log(f"  {description}: OK ({file_count} fichiers)", "SUCCESS")
                self.checks_passed.append(dir_name)
            else:
                self.log(f"  {description}: MANQUANT", "ERROR")
                self.problems.append(f"Missing directory: {dir_name} - {description}")

    def check_characters(self):
        """Vérifie les personnages"""
        self.log("\n👤 Vérification des personnages...", "INFO")

        chars_dir = self.base_path / "chars"
        if not chars_dir.exists():
            self.log("  Dossier chars manquant!", "ERROR")
            return

        # Compter les dossiers de personnages
        char_folders = [d for d in chars_dir.iterdir() if d.is_dir()]
        self.log(f"  Personnages trouvés: {len(char_folders)}", "SUCCESS")

        if len(char_folders) < 10:
            self.warnings.append(f"Only {len(char_folders)} characters - game may need more")
            self.log(f"  Peu de personnages ({len(char_folders)})", "WARNING")

        # Vérifier quelques personnages au hasard
        for char_dir in char_folders[:3]:
            def_files = list(char_dir.glob("*.def"))
            if def_files:
                self.log(f"    {char_dir.name}: OK", "SUCCESS")
            else:
                self.log(f"    {char_dir.name}: Pas de fichier .def", "WARNING")
                self.warnings.append(f"Character {char_dir.name} missing .def file")

    def check_stages(self):
        """Vérifie les stages"""
        self.log("\n🏟️  Vérification des stages...", "INFO")

        stages_dir = self.base_path / "stages"
        if not stages_dir.exists():
            self.log("  Dossier stages manquant!", "ERROR")
            return

        stage_files = list(stages_dir.glob("*.def"))
        self.log(f"  Stages trouvés: {len(stage_files)}", "SUCCESS")

        if len(stage_files) < 5:
            self.warnings.append(f"Only {len(stage_files)} stages - game may need more")
            self.log(f"  Peu de stages ({len(stage_files)})", "WARNING")

    def check_configuration(self):
        """Vérifie la configuration"""
        self.log("\n⚙️  Vérification de la configuration...", "INFO")

        cfg_path = self.base_path / "data/mugen.cfg"
        if not cfg_path.exists():
            self.log("  mugen.cfg manquant!", "ERROR")
            return

        try:
            with open(cfg_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Vérifier les sections importantes
            sections = ["[Options]", "[Config]", "[Video]", "[Sound]", "[Input]"]
            for section in sections:
                if section in content:
                    self.log(f"    {section}: OK", "SUCCESS")
                else:
                    self.log(f"    {section}: MANQUANT", "WARNING")
                    self.warnings.append(f"Configuration section {section} missing")

        except Exception as e:
            self.log(f"  Erreur lecture config: {e}", "ERROR")
            self.problems.append(f"Cannot read mugen.cfg: {e}")

    def check_dependencies(self):
        """Vérifie les dépendances Python"""
        self.log("\n🐍 Vérification des dépendances Python...", "INFO")

        required_modules = [
            ("pygame", "Gestion manette et audio"),
            ("PIL", "Traitement d'images"),
            ("pyautogui", "Automatisation"),
        ]

        for module, description in required_modules:
            try:
                __import__(module)
                self.log(f"  {module}: OK ({description})", "SUCCESS")
            except ImportError:
                self.log(f"  {module}: MANQUANT ({description})", "WARNING")
                self.warnings.append(f"Python module {module} not installed - install with: pip install {module}")

    def check_disk_space(self):
        """Vérifie l'espace disque"""
        self.log("\n💾 Vérification de l'espace disque...", "INFO")

        try:
            import shutil
            usage = shutil.disk_usage(self.base_path)

            total_gb = usage.total / (1024**3)
            used_gb = usage.used / (1024**3)
            free_gb = usage.free / (1024**3)

            self.log(f"  Espace libre: {free_gb:.1f} GB", "SUCCESS")

            if free_gb < 1:
                self.warnings.append(f"Low disk space: {free_gb:.1f} GB remaining")
                self.log(f"  Espace faible!", "WARNING")

        except Exception as e:
            self.log(f"  Impossible de vérifier: {e}", "WARNING")

    def check_tools(self):
        """Vérifie les outils créés"""
        self.log("\n🛠️  Vérification des outils...", "INFO")

        tools = [
            ("launcher.py", "Launcher principal"),
            ("ai_gamepad_configurator.py", "Configurateur manette IA"),
            ("ai_gamepad_navigator.py", "Navigateur manette IA"),
            ("gamepad_to_keyboard_mapper.py", "Mapper manette→clavier"),
            ("launcher_ai_navigator.py", "AI Navigator"),
        ]

        for tool, description in tools:
            tool_path = self.base_path / tool
            if tool_path.exists():
                self.log(f"  {description}: OK", "SUCCESS")
            else:
                self.log(f"  {description}: manquant", "WARNING")
                self.warnings.append(f"Tool {tool} missing")

    def generate_report(self):
        """Génère le rapport final"""
        self.log("\n" + "=" * 60, "INFO")
        self.log("📊 RAPPORT D'INSTALLATION", "INFO")
        self.log("=" * 60, "INFO")

        self.log(f"\n✓ Vérifications réussies: {len(self.checks_passed)}", "SUCCESS")
        self.log(f"⚠️  Avertissements: {len(self.warnings)}", "WARNING")
        self.log(f"❌ Problèmes critiques: {len(self.problems)}", "ERROR")

        if self.warnings:
            self.log("\n⚠️  AVERTISSEMENTS:", "WARNING")
            for i, warning in enumerate(self.warnings, 1):
                self.log(f"  {i}. {warning}", "WARNING")

        if self.problems:
            self.log("\n❌ PROBLÈMES CRITIQUES:", "ERROR")
            for i, problem in enumerate(self.problems, 1):
                self.log(f"  {i}. {problem}", "ERROR")

        # Sauvegarder le rapport
        report = {
            "timestamp": datetime.now().isoformat(),
            "checks_passed": self.checks_passed,
            "warnings": self.warnings,
            "problems": self.problems,
            "status": "OK" if len(self.problems) == 0 else "ISSUES_FOUND"
        }

        report_file = self.base_path / "installation_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        self.log(f"\n📄 Rapport sauvegardé: {report_file}", "SUCCESS")

        # Verdict final
        self.log("\n" + "=" * 60, "INFO")
        if len(self.problems) == 0:
            self.log("✓ INSTALLATION COMPLÈTE ET FONCTIONNELLE!", "SUCCESS")
            self.log("  Tous les fichiers essentiels sont présents.", "SUCCESS")
        else:
            self.log("⚠️  INSTALLATION INCOMPLÈTE", "WARNING")
            self.log("  Certains fichiers essentiels manquent.", "WARNING")
            self.log("  Consultez le rapport pour plus de détails.", "INFO")
        self.log("=" * 60, "INFO")

    def run(self):
        """Lance toutes les vérifications"""
        print("\n")
        print("=" * 60)
        print("🤖 IA VÉRIFICATEUR D'INSTALLATION ALL-IN-ONE")
        print("=" * 60)
        print()
        print("Cette IA va vérifier:")
        print("  • Fichiers essentiels")
        print("  • Dossiers requis")
        print("  • Personnages et stages")
        print("  • Configuration")
        print("  • Dépendances Python")
        print("  • Espace disque")
        print("  • Outils installés")
        print()

        self.check_essential_files()
        self.check_directories()
        self.check_characters()
        self.check_stages()
        self.check_configuration()
        self.check_dependencies()
        self.check_disk_space()
        self.check_tools()

        self.generate_report()

if __name__ == "__main__":
    checker = InstallationChecker()
    checker.run()

    print("\n")
    input("Appuyez sur Entrée pour quitter...")
