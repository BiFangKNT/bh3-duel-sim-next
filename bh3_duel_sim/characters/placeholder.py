"""占位角色实现."""

from __future__ import annotations

from typing import Callable, Tuple

from bh3_duel_sim.characters.base import BaseCharacter
from bh3_duel_sim.logger import BattleLogger
from bh3_duel_sim.stats import CombatStats


class PlaceholderCombatant(BaseCharacter):
    """占位用角色,用于验证框架."""

    def __init__(
        self,
        name: str,
        stats: CombatStats,
        active_cooldown: int = 3,
        bleed_damage: float = 25.0,
        passive_heal_ratio: float = 0.05,
    ) -> None:
        super().__init__(name, stats)
        self.active_cooldown = active_cooldown
        self.bleed_damage = bleed_damage
        self.passive_heal_ratio = passive_heal_ratio
        self._current_cooldown = 0

    def reset_for_battle(self) -> None:
        """重置冷却并调用父类重置."""
        super().reset_for_battle()
        self._current_cooldown = 0

    def apply_state_effects(self, opponent: BaseCharacter, logger: BattleLogger) -> None:
        """处理施加在自己身上的流血状态."""
        bleed = self.states.get("流血")
        if bleed:
            bleed["剩余回合"] -= 1
            logger.log(
                f"{self.name} 受到状态:流血 影响, 持续伤害 {bleed['伤害']:.2f} "
                f"(剩余 {bleed['剩余回合']} 回合)"
            )
            self.take_damage(bleed["伤害"], logger, "状态:流血")
            if bleed["剩余回合"] <= 0:
                logger.log(f"{self.name} 的流血状态结束")
                del self.states["流血"]

    def trigger_passive(self, opponent: BaseCharacter, logger: BattleLogger) -> bool:
        """被动技能: 每回合为自己回复固定比例生命."""
        heal_value = self.stats.max_hp * self.passive_heal_ratio
        logger.log(f"{self.name} 触发被动技能, 回复 {heal_value:.2f}")
        self.heal(heal_value, logger, "被动技能")
        return False

    def use_active_skill(self, opponent: BaseCharacter, logger: BattleLogger) -> bool:
        """主动技能: 冷却为 0 时造成额外伤害并叠加流血."""
        if self._current_cooldown > 0:
            self._current_cooldown -= 1
            return False
        self._current_cooldown = self.active_cooldown
        damage = self.effective_attack() * 1.5
        logger.log(f"{self.name} 释放主动技能, 造成 {damage:.2f} 并附加流血")
        opponent.take_damage(damage, logger, "主动技能")
        opponent.states["流血"] = {"伤害": self.bleed_damage, "剩余回合": 2}
        return True


def build_placeholder_fighters() -> Tuple[Callable[[], BaseCharacter], Callable[[], BaseCharacter]]:
    """构建可重复实例化的占位角色."""
    stats_a = CombatStats(max_hp=1500.0, attack=240.0, defense=60.0, speed=120.0)
    stats_b = CombatStats(max_hp=1650.0, attack=220.0, defense=80.0, speed=110.0)

    def spawn_a() -> BaseCharacter:
        return PlaceholderCombatant(
            name="代号红",
            stats=stats_a,
            active_cooldown=2,
            bleed_damage=30.0,
            passive_heal_ratio=0.04,
        )

    def spawn_b() -> BaseCharacter:
        return PlaceholderCombatant(
            name="代号蓝",
            stats=stats_b,
            active_cooldown=3,
            bleed_damage=20.0,
            passive_heal_ratio=0.06,
        )

    return spawn_a, spawn_b
