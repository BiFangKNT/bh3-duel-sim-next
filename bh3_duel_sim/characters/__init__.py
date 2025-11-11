"""角色子包导出."""

from .base import BaseCharacter
from .placeholder import PlaceholderCombatant, build_placeholder_fighters
from .valkyries import *  # noqa: F401,F403
from .valkyries import __all__ as _VALKYRIE_EXPORTS
from .valkyries import build_valkyrie_roster

__all__ = [
    "BaseCharacter",
    "PlaceholderCombatant",
    "build_placeholder_fighters",
    "build_valkyrie_roster",
]
__all__.extend(_VALKYRIE_EXPORTS)  # pyright: ignore[reportUnsupportedDunderAll]
