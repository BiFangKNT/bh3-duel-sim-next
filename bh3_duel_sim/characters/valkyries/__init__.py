"""女武神角色包."""

from __future__ import annotations

from typing import Callable

from ..base import BaseCharacter
from .bianka import Bianka
from .bronya import Bronya
from .chenxue import Chenxue
from .kiana import Kiana
from .korali import Korali
from .lita import Lita


def build_valkyrie_roster() -> dict[str, Callable[[], BaseCharacter]]:
    """提供默认女武神角色工厂."""
    return {
        "科拉莉": Korali,
        "布洛妮娅": Bronya,
        "比安卡": Bianka,
        "琪亚娜": Kiana,
        "晨雪": Chenxue,
        "丽塔": Lita,
    }


__all__ = [
    "Korali",
    "Bronya",
    "Bianka",
    "Kiana",
    "Chenxue",
    "Lita",
    "build_valkyrie_roster",
]
