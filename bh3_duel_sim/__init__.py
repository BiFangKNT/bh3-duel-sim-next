"""对战模拟核心包."""

from .characters.base import BaseCharacter
from .characters.placeholder import PlaceholderCombatant, build_placeholder_fighters
from .characters.valkyries import (
    Bianka,
    Bronya,
    Kiana,
    Korali,
    build_valkyrie_roster,
)
from .logger import BattleLogger
from .simulator import (
    BattleSimulator,
    mass_battle_statistics,
    round_robin_statistics,
    run_single_verbose_battle,
)
from .stats import CombatStats

__all__ = [
    "BaseCharacter",
    "PlaceholderCombatant",
    "build_placeholder_fighters",
    "Korali",
    "Bronya",
    "Bianka",
    "Kiana",
    "build_valkyrie_roster",
    "BattleLogger",
    "BattleSimulator",
    "mass_battle_statistics",
    "round_robin_statistics",
    "run_single_verbose_battle",
    "CombatStats",
]
