"""战斗属性定义模块."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CombatStats:
    """角色基础属性."""

    max_hp: float
    attack: float
    defense: float
    speed: float
