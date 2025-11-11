"""角色定义."""

from __future__ import annotations

from ...logger import BattleLogger
from ...stats import CombatStats
from ..base import BaseCharacter


class Chenxue(BaseCharacter):
    """晨雪: 以血换防的持续战士."""

    LOW_HP_THRESHOLD = 30.0
    LOW_HP_HEAL = 5.0

    def __init__(self) -> None:
        self._base_stats = CombatStats(max_hp=100.0, attack=16.0, defense=8.0, speed=21.0)
        super().__init__(name="晨雪", stats=self._base_stats)
        self.configure_active_cooldown(2)
        self._stunned = False
        self._confused = False
        self._prebattle_defense_penalty = self._base_stats.defense * 0.15
        self._prebuff_logged = False

    def reset_for_battle(self) -> None:
        super().reset_for_battle()
        self.set_max_hp_override(self._base_stats.max_hp * 1.5)
        self.current_hp = self.max_hp
        self.bonus_defense -= self._prebattle_defense_penalty
        self._stunned = False
        self._confused = False
        self._prebuff_logged = False

    def apply_state_effects(self, opponent: BaseCharacter, logger: BattleLogger) -> None:
        if not self._prebuff_logged:
            self.log_action(logger, "passive", "被动触发: 生命上限+50%, 防御-15%")
            self._prebuff_logged = True
        self._stunned = False
        self._confused = False
        self._handle_bleed(logger)
        self._handle_stun(logger)
        self._handle_confusion(logger)
        self._handle_defense_break(logger)
        if self.current_hp < self.LOW_HP_THRESHOLD:
            self.log_action(logger, "passive", "触发低血回复, 恢复 5 点生命")
            self.heal(self.LOW_HP_HEAL, logger, "被动技能")

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
                f"陷入眩晕, 本回合无法发动主动或普攻 (剩余 {remaining} 回合)",
            )

        self.process_state("眩晕", logger, effect, end_message=f"{self.name} 的眩晕状态结束")

    def _handle_confusion(self, logger: BattleLogger) -> None:
        def effect(_: dict[str, float], remaining: int) -> None:
            self._confused = True
            self.log_action(
                logger, "state", f"陷入混乱, 普攻会转而攻击自己 (剩余 {remaining} 回合)"
            )

        self.process_state("混乱", logger, effect, end_message=f"{self.name} 的混乱状态结束")

    def trigger_passive(self, opponent: BaseCharacter, logger: BattleLogger) -> bool:
        if self._stunned:
            self.log_action(logger, "state", "因眩晕跳过本回合的主动与普攻")
            return True
        return False

    def use_active_skill(self, opponent: BaseCharacter, logger: BattleLogger) -> bool:
        if not self.consume_active_charge():
            return False
        lost_hp = self.max_hp - self.current_hp
        bonus_damage = lost_hp * 0.12 + 8.0
        attack_value = self.effective_attack() + bonus_damage
        mitigated = max(0.0, attack_value - opponent.effective_defense())
        total_damage = max(1.0, mitigated)
        self.log_action(
            logger,
            "active",
            f"发动残心突袭, 造成 {total_damage:.2f} (失血加成 {bonus_damage:.2f})",
        )
        opponent.take_damage(total_damage, logger, "主动技能", attacker=self)
        return False

    def perform_basic_attack(self, opponent: BaseCharacter, logger: BattleLogger) -> None:
        if self._confused:
            damage = max(
                0.05 * self.effective_attack(),
                self.effective_attack() - self.effective_defense(),
            )
            self.log_action(logger, "state", f"因混乱自击, 预计伤害 {damage:.2f}")
            self.take_damage(damage, logger, "混乱误伤")
            return
        super().perform_basic_attack(opponent, logger)
