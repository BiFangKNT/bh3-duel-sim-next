"""对战模拟核心包."""

from bh3_duel_sim.characters.base import BaseCharacter
from bh3_duel_sim.characters.placeholder import PlaceholderCombatant, build_placeholder_fighters
from bh3_duel_sim.logger import BattleLogger
from bh3_duel_sim.simulator import BattleSimulator, mass_battle_statistics, run_single_verbose_battle
from bh3_duel_sim.stats import CombatStats

__all__ = [
    "BaseCharacter",
    "PlaceholderCombatant",
    "build_placeholder_fighters",
    "BattleLogger",
    "BattleSimulator",
    "mass_battle_statistics",
    "run_single_verbose_battle",
    "CombatStats",
]
