"""女武神角色包."""

from __future__ import annotations

import importlib
import inspect
import pkgutil
from typing import Callable, cast

from ..base import BaseCharacter

_VALKYRIE_CLASSES: dict[str, type[BaseCharacter]] = {}

for module_info in pkgutil.iter_modules(__path__):
    module = importlib.import_module(f"{__name__}.{module_info.name}")
    for attr_name, attr in inspect.getmembers(module, inspect.isclass):
        if (
            issubclass(attr, BaseCharacter)
            and attr is not BaseCharacter
            and attr.__module__ == module.__name__
        ):
            _VALKYRIE_CLASSES[attr_name] = attr

for class_name, class_obj in _VALKYRIE_CLASSES.items():
    globals()[class_name] = class_obj

__all__ = list(_VALKYRIE_CLASSES.keys()) + ["build_valkyrie_roster"]  # pyright: ignore[reportUnsupportedDunderAll]


def build_valkyrie_roster() -> dict[str, Callable[[], BaseCharacter]]:
    """提供默认女武神角色工厂."""
    roster: dict[str, Callable[[], BaseCharacter]] = {}
    for cls in _VALKYRIE_CLASSES.values():
        factory = cast("Callable[[], BaseCharacter]", cls)
        instance = factory()
        roster[instance.name] = factory
    return roster
