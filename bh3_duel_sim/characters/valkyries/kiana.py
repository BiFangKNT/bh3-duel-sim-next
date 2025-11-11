"""角色定义."""

from __future__ import annotations

from ...logger import BattleLogger
from ...stats import CombatStats
from ..base import BaseCharacter


class Kiana(BaseCharacter):
    """琪亚娜: 主动爆发附带生命百分比真实伤害."""

    def __init__(self) -> None:
        super().__init__(
            name="琪亚娜",
            stats=CombatStats(max_hp=100.0, attack=18.0, defense=7.0, speed=21.0),
        )
        self.configure_active_cooldown(2)
        self._stunned = False
        self._confused = False

    def reset_for_battle(self) -> None:
        super().reset_for_battle()
        self._stunned = False
        self._confused = False

    def apply_state_effects(self, opponent: BaseCharacter, logger: BattleLogger) -> None:
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
                f"陷入眩晕, 本回合无法发动主动或普攻 (剩余 {remaining} 回合)",
            )

        self.process_state("眩晕", logger, effect, end_message=f"{self.name} 的眩晕状态结束")

    def _handle_confusion(self, logger: BattleLogger) -> None:
        def effect(_: dict[str, float], remaining: int) -> None:
            self._confused = True
            self.log_action(
                logger,
                "state",
                f"陷入混乱, 普攻会转而攻击自己 (剩余 {remaining} 回合)",
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
        if opponent.is_alive and not self.is_passive_blocked():
            bonus = max(1.0, opponent.current_hp * 0.15)
            self.log_action(logger, "passive", f"被动发动, 先造成 {bonus:.2f} 点真实伤害")
            opponent.take_damage(bonus, logger, "被动:超限打击", ignore_shield=True, attacker=self)
        if opponent.is_alive:
            damage = self.calculate_skill_damage(20.0, opponent)
            self.log_action(logger, "active", f"主动追加 20 点伤害, 预期 {damage:.2f}")
            opponent.take_damage(damage, logger, "主动技能", attacker=self)
        return False

    def perform_basic_attack(self, opponent: BaseCharacter, logger: BattleLogger) -> None:
        if self._confused:
            damage = max(
                0.05 * self.effective_attack(),
                self.effective_attack() - self.effective_defense(),
            )
            self.log_action(logger, "state", f"因混乱攻击自己, 预计伤害 {damage:.2f}")
            self.take_damage(damage, logger, "混乱误伤")
            return
        super().perform_basic_attack(opponent, logger)
