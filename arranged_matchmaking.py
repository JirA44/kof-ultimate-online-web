"""
Arranged Matchmaking System for KOF Ultimate Online
Pure Python simulation of IA vs IA matches without GUI automation.
Selects two characters from the 188 available and runs simulated battles.
Used for tournament seeding, balance testing, and AI vs AI match analysis.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import random
import json
from pathlib import Path


@dataclass
class Character:
    """Represents a playable KOF character with AI strategy profile."""
    id: str
    name: str
    category: str  # "rushdown", "zoning", "grapple", "mixup", "defense", etc.
    tier: float  # 0.0 to 1.0, higher = stronger/ more competitive
    playstyle: str  # aggressive, defensive, balanced, zoning, rushdown, grapple
    strengths: List[str]
    weaknesses: List[str]


@dataclass
class MatchResult:
    """Result of a simulated match between two characters."""
    character_a: Character
    character_b: Character
    winner: Optional[Character]
    duration_frames: int
    winner_margin: float  # percentage difference in performance (-1.0 to 1.0)
    conditions: Dict[str, any]


class MatchmakingEngine:
    """Engine for arranging and simulating KOF matches between IA characters."""

    def __init__(self, characters: List[Character], seed: Optional[int] = None):
        self.characters = characters
        self.rng = random.Random(seed)
        self.results: List[MatchResult] = []
        self.character_map: Dict[str, Character] = {
            c.id: c for c in characters
        }

    def select_opponents(
        self,
        count: int = 2,
        criteria: Optional[Dict[str, str]] = None,
    ) -> List[Character]:
        """Select characters based on criteria (tier, category, playstyle)."""
        pool = list(self.characters)

        if criteria:
            key = criteria.get("category")
            if key and key != "any":
                pool = [c for c in pool if c.category == key]

            key = criteria.get("min_tier")
            if key:
                min_tier = float(key)
                pool = [c for c in pool if c.tier >= min_tier]

            key = criteria.get("max_tier")
            if key:
                max_tier = float(key)
                pool = [c for c in pool if c.tier <= max_tier]

            key = criteria.get("playstyle")
            if key and key != "any":
                pool = [c for c in pool if c.playstyle == key]

        if len(pool) < count:
            pool = list(self.characters)

        selected = self.rng.sample(pool, min(count, len(pool)))
        return selected

    def simulate_battle(
        self,
        char_a: Character,
        char_b: Character,
        rounds: int = 3,
    ) -> MatchResult:
        """Simulate a battle between two characters using tier and playstyle mechanics."""
        a_wins = 0
        b_wins = 0
        total_frames = 0

        for _ in range(rounds):
            # Base advantage from tier difference
            tier_diff = char_a.tier - char_b.tier

            # Playstyle matchup factor (rock-paper-scissors style)
            playstyle_factor = self._calculate_playstyle_factor(char_a, char_b)

            # Combined weight: tier contributes 50%, playstyle 30%, random 20%
            outcome_weight = tier_diff * 0.5 + playstyle_factor * 0.3

            # Randomized outcome with tier/playstyle influence
            # Outcome > threshold means character_a wins the round
            threshold = 0.15 - outcome_weight * 0.3
            outcome = self.rng.random()

            if outcome > threshold:
                a_wins += 1
            else:
                b_wins += 1

            # Estimate frames per KOF round (~120-180 frames)
            total_frames += self.rng.randint(120, 180)

        # Determine overall winner
        winner = None
        if a_wins > b_wins:
            winner = char_a
        elif b_wins > a_wins:
            winner = char_b

        # Calculate margin of victory
        total = a_wins + b_wins
        winner_margin = (a_wins - b_wins) / total if total > 0 else 0.0

        # Clamp margin to [-1, 1]
        winner_margin = max(-1.0, min(1.0, winner_margin))

        result = MatchResult(
            character_a=char_a,
            character_b=char_b,
            winner=winner,
            duration_frames=total_frames,
            winner_margin=winner_margin,
            conditions={
                "rounds": rounds,
                "a_wins": a_wins,
                "b_wins": b_wins,
                "tier_diff": char_a.tier - char_b.tier,
                "playstyle_factor": playstyle_factor,
            },
        )

        self.results.append(result)
        return result

    def _calculate_playstyle_factor(
        self, attacker: Character, defender: Character
    ) -> float:
        """Calculate playstyle matchup advantage using interaction matrix."""
        # Rock-paper-scissors style matchup advantages
        interaction_matrix = {
            ("rushdown", "zoning"): 0.10,
            ("zoning", "grapple"): 0.15,
            ("grapple", "rushdown"): 0.10,
            ("mixup", "rushdown"): -0.05,
            ("rushdown", "mixup"): 0.05,
            ("mixup", "zoning"): 0.08,
            ("zoning", "mixup"): -0.08,
            ("grapple", "mixup"): 0.05,
            ("mixup", "grapple"): -0.05,
        }

        key = (attacker.playstyle, defender.playstyle)
        reverse_key = (defender.playstyle, attacker.playstyle)

        if key in interaction_matrix:
            return interaction_matrix[key]
        if reverse_key in interaction_matrix:
            return -interaction_matrix[reverse_key]
        return 0.0

    def run_tournament(
        self,
        format: str = "round_robin",
        rounds_per_match: int = 3,
    ) -> Dict[str, any]:
        """Run a full tournament or round-robin tournament."""
        results: Dict[str, any] = {}
        n = len(self.characters)

        if format == "round_robin":
            # Every character faces every other character exactly once
            for i in range(n):
                for j in range(i + 1, n):
                    char_a = self.characters[i]
                    char_b = self.characters[j]
                    result = self.simulate_battle(char_a, char_b, rounds_per_match)
                    key = f"{char_a.id}_{char_b.id}"
                    results[key] = {
                        "character_a": char_a.name,
                        "character_b": char_b.name,
                        "winner": result.winner.name if result.winner else "Draw",
                        "a_wins": result.conditions["a_wins"],
                        "b_wins": result.conditions["b_wins"],
                        "margin": result.winner_margin,
                        "duration_frames": result.duration_frames,
                    }

        elif format == "single_elimination":
            # Simplified single-elimination bracket
            remaining = list(enumerate(self.characters))
            round_num = 0

            while len(remaining) > 1:
                random.shuffle(remaining)
                next_round = []

                for i in range(0, len(remaining) - 1, 2):
                    idx_a, char_a = remaining[i]
                    idx_b, char_b = remaining[i + 1]
                    result = self.simulate_battle(char_a, char_b, rounds_per_match)
                    winner = result.winner

                    key = f"{char_a.id}_{char_b.id}"
                    results[key] = {
                        "character_a": char_a.name,
                        "character_b": char_b.name,
                        "winner": winner.name if winner else "Draw",
                        "margin": result.winner_margin,
                        "duration_frames": result.duration_frames,
                    }

                    if winner:
                        next_round.append((idx_a if winner == char_a else idx_b, winner))
                    else:
                        # Draw: advance lower-tier character
                        next_round.append(
                            (idx_a if char_a.tier >= char_b.tier else idx_b, char_a if char_a.tier >= char_b.tier else char_b)
                        )

                remaining = next_round
                round_num += 1

        elif format == "double_elimination":
            # Double elimination bracket (simplified)
            winners_bracket = list(enumerate(self.characters))
            losers_bracket: List[Tuple[int, Character]] = []

            while len(winners_bracket) > 1:
                random.shuffle(winners_bracket)
                next_winners = []

                for i in range(0, len(winners_bracket) - 1, 2):
                    idx_a, char_a = winners_bracket[i]
                    idx_b, char_b = winners_bracket[i + 1]
                    result = self.simulate_battle(char_a, char_b, rounds_per_match // 2)
                    winner = result.winner

                    key = f"{char_a.id}_{char_b.id}_winners"
                    results[key] = {
                        "character_a": char_a.name,
                        "character_b": char_b.name,
                        "winner": winner.name if winner else "Draw",
                        "bracket": "winners",
                        "margin": result.winner_margin,
                    }

                    if winner:
                        next_winners.append((idx_a if winner == char_a else idx_b, winner))
                    else:
                        next_winners.append(
                            (idx_a if char_a.tier >= char_b.tier else idx_b, char_a if char_a.tier >= char_b.tier else char_b)
                        )

                # Move losers to losers bracket
                eliminated = [c for i, c in winners_bracket if i % 2 == 0 and i + 1 < len(winners_bracket)]
                losers_bracket.extend([(i, c) for i, c in winners_bracket if i % 2 == 1])

                winners_bracket = next_winners

            # Final between winners bracket winner and losers bracket winner
            if winners_bracket and losers_bracket:
                idx_winner, char_winner = winners_bracket[0]
                idx_eliminated, char_eliminated = losers_bracket[0]

                result = self.simulate_battle(char_winner, char_eliminated, rounds_per_match)
                winner = result.winner

                key = f"{char_winner.id}_{char_eliminated.id}_final"
                results[key] = {
                    "character_a": char_winner.name,
                    "character_b": char_eliminated.name,
                    "winner": winner.name if winner else "Draw",
                    "bracket": "final",
                    "margin": result.winner_margin,
                }

        # Calculate rankings from all match results
        rankings = self._calculate_rankings(results, n)
        return {
            "format": format,
            "results": results,
            "rankings": rankings,
            "total_matches": len(results),
            "total_characters": n,
        }

    def _calculate_rankings(
        self, results: Dict, total_chars: int
    ) -> List[Dict[str, any]]:
        """Calculate player rankings from match results."""
        stats: Dict[str, Dict[str, any]] = {}
        for char in self.characters:
            stats[char.id] = {
                "name": char.name,
                "total_matches": 0,
                "wins": 0,
                "losses": 0,
                "draws": 0,
                "win_rate": 0.0,
                "average_margin": 0.0,
                "total_margin": 0.0,
            }

        for key, result in results.items():
            # Parse character IDs from key (format: "charA_id_charB_id" or "charA_id_charB_id_bracket")
            parts = key.split("_")
            a_id = parts[0]
            b_id = parts[1]

            if a_id in stats:
                stats[a_id]["total_matches"] += 1
                if result.get("winner") == stats[a_id]["name"]:
                    stats[a_id]["wins"] += 1
                elif result.get("winner") is not None and result.get("winner") != stats[a_id]["name"]:
                    stats[a_id]["losses"] += 1
                else:
                    stats[a_id]["draws"] += 1

            if b_id in stats:
                stats[b_id]["total_matches"] += 1
                if result.get("winner") == stats[b_id]["name"]:
                    stats[b_id]["wins"] += 1
                elif result.get("winner") is not None and result.get("winner") != stats[b_id]["name"]:
                    stats[b_id]["losses"] += 1
                else:
                    stats[b_id]["draws"] += 1

        # Calculate derived metrics
        ranking_list = []
        for char_id, s in stats.items():
            if s["total_matches"] > 0:
                s["win_rate"] = s["wins"] / s["total_matches"]
                s["average_margin"] = s["total_margin"] / s["total_matches"]
            else:
                s["win_rate"] = 0.5  # neutral default
                s["average_margin"] = 0.0
            ranking_list.append(s)

        # Sort by win rate (desc), then by total matches (desc) as tiebreaker
        ranking_list.sort(key=lambda x: (x["win_rate"], x["total_matches"]), reverse=True)
        return ranking_list

    def export_results(self, filepath: Path, format: str = "json") -> None:
        """Export match results to file in specified format."""
        data = {
            "total_characters": len(self.characters),
            "total_matches": len(self.results),
            "engine_seed": self.rng.randint(0, 2**31),
            "results": [
                {
                    "character_a": r.character_a.name,
                    "character_b": r.character_b.name,
                    "winner": r.winner.name if r.winner else "Draw",
                    "duration_frames": r.duration_frames,
                    "winner_margin": r.winner_margin,
                    "conditions": r.conditions,
                }
                for r in self.results
            ],
        }

        with open(filepath, "w", encoding="utf-8") as f:
            if format == "json":
                json.dump(data, f, indent=2, ensure_ascii=False)
            elif format == "csv":
                f.write("Character A,Character B,Winner,DurationFrames,WinnerMargin\n")
                for r in data["results"]:
                    winner_name = r["winner"] if r["winner"] != "Draw" else ""
                    f.write(
                        f"{r['character_a']},{r['character_b']},{winner_name},"
                        f"{r['duration_frames']},{r['winner_margin']}\n"
                    )
            elif format == "txt":
                f.write(self._format_text_report(data))

    def _format_text_report(self, data: Dict) -> str:
        """Format results as human-readable text report."""
        lines = [
            f"KOF Ultimate Online - Arranged Matchmaking Report",
            f"=" * 50,
            f"Total Characters: {data['total_characters']}",
            f"Total Matches: {data['total_matches']}",
            f"Engine Seed: {data['engine_seed']}",
            "",
            "Match Results:",
            "-" * 50,
        ]

        for r in data["results"]:
            winner_str = r["winner"] if r["winner"] != "Draw" else "Empate"
            lines.append(
                f"  {r['character_a']:20s} vs {r['character_b']:20s} | "
                f"Ganador: {winner_str:10s} | "
                f"Frames: {r['duration_frames']:3d} | "
                f"Margen: {r['winner_margin']:.2%}"
            )

        lines.extend([
            "",
            "Rankings:",
            "-" * 50,
        ])

        for i, r in enumerate(data["rankings"][:10], 1):
            lines.append(
                f"  {i}. {r['name']:20s} | "
                f"Win Rate: {r['win_rate']:.1%} | "
                f"Matches: {r['total_matches']}"
            )

        return "\n".join(lines)


# Default dataset of 188 KOF characters (sample - full dataset would be loaded from external file)
DEFAULT_CHARACTERS: List[Character] = [
    # Core KOF XIV/XV characters (first 20 for demonstration)
    Character(id="kof001", name="Kyo Kusanagi", category="rushdown", tier=0.85, playstyle="rushdown",
              strengths=["fast attacks", "combo potential"], weaknesses=["poor defense on block"]),
    Character(id="kof002", name="Iori Yagami", category="grapple", tier=0.82, playstyle="grapple",
              strengths=["high damage", "pressure"], weaknesses=["slow startup"]),
    Character(id="kof003", name="Terry Bogard", category="rushdown", tier=0.88, playstyle="rushdown",
              strengths=["versatile", "good meter management"], weaknesses=["mediocre zoning"]),
    Character(id="kof004", name="Mai Shiranui", category="rushdown", tier=0.80, playstyle="rushdown",
              strengths=["fast", "good footsies"], weaknesses=["low defense"]),
    Character(id="kof005", name="Kasumi", category="rushdown", tier=0.78, playstyle="rushdown",
              strengths=["high mobility"], weaknesses=["low health"]),
    Character(id="kof006", name="Andy Bogard", category="grapple", tier=0.75, playstyle="grapple",
              strengths=["good grab range"], weaknesses=["slow moves"]),
    Character(id="kof007", name="Bailey", category="zoning", tier=0.72, playstyle="zoning",
              strengths=["projectiles", "keepaway"], weaknesses=["close range"]),
Character(id="kof008", name="Luong", category="mixup", tier=0.76, playstyle="mixup",
          strengths=["unblockable mixups"], weaknesses=["predictable"]),
Character(id="kof009", name="Mian", category="defense", tier=0.74, playstyle="defensive",
          strengths=["good block", "punish on whiff"], weaknesses=["low damage"]),
    Character(id="kof010", name="K", category="rushdown", tier=0.87, playstyle="rushdown",
              strengths=["high damage"], weaknesses=["resource management"]),
    # ... truncated for brevity - full 188 characters would be in dataset file
]

# Mapping of category playstyle constants
CATEGORY_RUSHDOWN = "rushdown"
CATEGORY_ZONING = "zoning"
CATEGORY_GRAPPLE = "grapple"
CATEGORY_MIXUP = "mixup"
CATEGORY_DEFENSE = "defensive"

# Elemental/property tags for advanced matching
CHARACTER_PROPERTIES = {
    # Properties that affect matchup calculations
    "projectile": 0.10,
    "grab": 0.15,
    "low_profile": 0.08,
    "high_damage": 0.12,
    "meter_gain": 0.07,
}


def load_characters_from_dataset(dataset_path: Path) -> List[Character]:
    """Load character dataset from JSON file."""
    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [Character(**c) for c in data.get("characters", [])]


def create_engine_from_dataset(dataset_path: Optional[Path] = None) -> MatchmakingEngine:
    """Create a matchmaking engine loaded from character dataset."""
    if dataset_path and dataset_path.exists():
        characters = load_characters_from_dataset(dataset_path)
    else:
        characters = DEFAULT_CHARACTERS

    return MatchmakingEngine(characters)


def quick_match(
    char_a_name: str,
    char_b_name: str,
    rounds: int = 3,
    engine: Optional[MatchmakingEngine] = None,
) -> MatchResult:
    """Run a quick match between two named characters."""
    eng = engine or create_engine_from_dataset()

    char_a = eng.character_map.get(char_a_name)
    char_b = eng.character_map.get(char_b_name)

    if not char_a or not char_b:
        # Try fuzzy match
        for c in eng.characters:
            if char_a_name.lower() in c.name.lower():
                char_a = c
            if char_b_name.lower() in c.name.lower():
                char_b = c

    if not char_a or not char_b:
        raise ValueError(f"Characters not found: {char_a_name}, {char_b_name}")

    return eng.simulate_battle(char_a, char_b, rounds)


if __name__ == "__main__":
    # Example usage
    import sys

    engine = create_engine_from_dataset()

    print("=" * 60)
    print("KOF Ultimate Online - Arranged Matchmaking Demo")
    print("=" * 60)

    # Select two random rushdown characters
    opponents = engine.select_opponents(criteria={"category": "rushdown"})
    print(f"\nSelected: {opponents[0].name} vs {opponents[1].name}")

    # Simulate best-of-5 match
    result = engine.simulate_battle(opponents[0], opponents[1], rounds=5)
    print(f"Result: {result.winner.name if result.winner else 'Draw'} wins")
    print(f"Margin: {result.winner_margin:.2%}")
    print(f"Duration: {result.duration_frames} frames")
    print(f"Conditions: {result.conditions}")

    # Run round-robin tournament
    print("\n--- Round-Robin Tournament ---")
    tournament = engine.run_tournament(format="round_robin", rounds_per_match=3)
    print(f"Total matches: {tournament['total_matches']}")
    print(f"Total characters: {tournament['total_characters']}")

    print("\nTop 5 Rankings:")
    for i, r in enumerate(tournament["rankings"][:5]):
        print(f"  {i+1}. {r['name']}: {r['win_rate']:.1%} win rate ({r['total_matches']} matches)")

    # Export results
    export_path = Path("match_results.json")
    engine.export_results(export_path)
    print(f"\nResults exported to: {export_path}")

    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)