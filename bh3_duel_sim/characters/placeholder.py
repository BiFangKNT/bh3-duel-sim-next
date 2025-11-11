"""占位角色实现."""

from __future__ import annotations

from typing import Callable

from ..logger import BattleLogger
from ..stats import CombatStats
from .base import BaseCharacter


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
        self.configure_active_cooldown(active_cooldown)
        self.bleed_damage = bleed_damage
        self.passive_heal_ratio = passive_heal_ratio
        self._stunned = False
        self._confused = False

    def reset_for_battle(self) -> None:
        """重置冷却并调用父类重置."""
        super().reset_for_battle()
        self._stunned = False
        self._confused = False

    def apply_state_effects(self, opponent: BaseCharacter, logger: BattleLogger) -> None:
        """处理施加在自己身上的流血/眩晕/混乱."""
        self._stunned = False
        self._confused = False
        self._handle_bleed(logger)
        self._handle_stun(logger)
        self._handle_confusion(logger)
        self._handle_defense_break(logger)

    def _handle_bleed(self, logger: BattleLogger) -> None:
        def effect(state: dict[str, float], remaining: int) -> None:
            self.log_action(
                logger,
                "state",
                f"受到状态:流血 影响, 持续伤害 {state['伤害']:.2f} (剩余 {remaining} 回合)",
            )
            self.take_damage(state["伤害"], logger, "状态:流血")

        self.process_state("流血", logger, effect, end_message=f"{self.name} 的流血状态结束")

    def _handle_stun(self, logger: BattleLogger) -> None:
        def effect(_: dict[str, float], remaining: int) -> None:
            self._stunned = True
            self.log_action(
                logger,
                "state",
                f"受到状态:眩晕 影响, 本回合无法发动主动或普攻 (剩余 {remaining} 回合)",
            )

        self.process_state("眩晕", logger, effect, end_message=f"{self.name} 的眩晕状态结束")

    def _handle_confusion(self, logger: BattleLogger) -> None:
        def effect(_: dict[str, float], remaining: int) -> None:
            self._confused = True
            self.log_action(logger, "state", f"陷入混乱, 普攻会伤害自己 (剩余 {remaining} 回合)")

        self.process_state("混乱", logger, effect, end_message=f"{self.name} 的混乱状态结束")

    def trigger_passive(self, opponent: BaseCharacter, logger: BattleLogger) -> bool:
        """被动技能: 每回合为自己回复固定比例生命."""
        heal_value = self.max_hp * self.passive_heal_ratio
        self.log_action(logger, "passive", f"触发被动技能, 回复 {heal_value:.2f}")
        self.heal(heal_value, logger, "被动技能")
        if self._stunned:
            self.log_action(logger, "state", "因眩晕无法发动主动或普攻")
            return True
        return False

    def use_active_skill(self, opponent: BaseCharacter, logger: BattleLogger) -> bool:
        """主动技能: 冷却为 0 时造成额外伤害并叠加流血."""
        if not self.consume_active_charge():
            return False
        damage = self.calculate_skill_damage(self.effective_attack() * 1.5, opponent)
        self.log_action(logger, "active", f"释放主动技能, 造成 {damage:.2f} 并附加流血")
        opponent.take_damage(damage, logger, "主动技能", attacker=self)
        opponent.apply_state("流血", {"伤害": self.bleed_damage, "剩余回合": 2}, logger)
        return True

    def perform_basic_attack(self, opponent: BaseCharacter, logger: BattleLogger) -> None:
        """在混乱时自伤,否则沿用默认普攻."""
        if self._confused:
            damage = max(
                0.05 * self.effective_attack(),
                self.effective_attack() - self.effective_defense(),
            )
            self.log_action(logger, "state", f"因混乱误伤自己, 预计伤害 {damage:.2f}")
            self.take_damage(damage, logger, "混乱误伤")
            return
        super().perform_basic_attack(opponent, logger)


def build_placeholder_fighters() -> tuple[Callable[[], BaseCharacter], Callable[[], BaseCharacter]]:
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
