"""对战模拟核心包."""

from .characters import *  # noqa: F401,F403
from .characters import (
    BaseCharacter,
    PlaceholderCombatant,
    build_placeholder_fighters,
    build_valkyrie_roster,
)
from .characters import __all__ as _CHARACTERS_EXPORTS
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
    "build_valkyrie_roster",
    "BattleLogger",
    "BattleSimulator",
    "mass_battle_statistics",
    "round_robin_statistics",
    "run_single_verbose_battle",
    "CombatStats",
]
__all__.extend(name for name in _CHARACTERS_EXPORTS if name not in __all__)
