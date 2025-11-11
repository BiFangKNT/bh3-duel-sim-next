"""角色定义."""

from __future__ import annotations

from ...logger import BattleLogger
from ...stats import CombatStats
from ..base import BaseCharacter


class Bianka(BaseCharacter):
    """比安卡: 护盾堆叠与追加斩击."""

    def __init__(self) -> None:
        super().__init__(
            name="比安卡",
            stats=CombatStats(max_hp=100.0, attack=16.0, defense=11.0, speed=22.0),
        )
        self.configure_active_cooldown(2)
        self._shield_value = 0.0
        self._stunned = False
        self._confused = False

    def reset_for_battle(self) -> None:
        super().reset_for_battle()
        self._shield_value = 0.0
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

    def _gain_shield(self, logger: BattleLogger) -> None:
        self._shield_value += 5.0
        self.log_action(
            logger,
            "passive",
            f"的被动生效, 获得 5 点护盾 -> 当前 {self._shield_value:.2f}",
        )

    def _maybe_bonus_slash(self, opponent: BaseCharacter, logger: BattleLogger) -> None:
        if not opponent.is_alive:
            return
        if self.roll_chance(0.20):
            damage = self.calculate_skill_damage(24.0, opponent)
            self.log_action(
                logger,
                "active",
                f"的主动追加斩击触发, 额外造成 {damage:.2f} (不计入被动)",
            )
            opponent.take_damage(damage, logger, "主动技能追加", attacker=self)

    def use_active_skill(self, opponent: BaseCharacter, logger: BattleLogger) -> bool:
        if not self.consume_active_charge():
            return False
        damage = self.calculate_skill_damage(16.0, opponent)
        self.log_action(logger, "active", f"以主动替换普攻, 造成 {damage:.2f} 伤害")
        opponent.take_damage(damage, logger, "主动技能", attacker=self)
        self._gain_shield(logger)
        self._maybe_bonus_slash(opponent, logger)
        return True

    def take_damage(
        self,
        amount: float,
        logger: BattleLogger,
        source: str,
        *,
        ignore_shield: bool = False,
        attacker: BaseCharacter | None = None,
    ) -> None:
        if not ignore_shield and self._shield_value > 0 and amount > 0:
            absorbed = min(amount, self._shield_value)
            self._shield_value -= absorbed
            self.log_action(
                logger,
                "state",
                f"的护盾吸收 {absorbed:.2f} 点伤害 -> 剩余护盾 {self._shield_value:.2f}",
            )
            amount -= absorbed
        if amount <= 0:
            return
        super().take_damage(amount, logger, source, ignore_shield=ignore_shield, attacker=attacker)

    def perform_basic_attack(self, opponent: BaseCharacter, logger: BattleLogger) -> None:
        if self._confused:
            damage = max(
                0.05 * self.effective_attack(),
                self.effective_attack() - self.effective_defense(),
            )
            self.log_action(logger, "state", f"因混乱攻击自己, 预计伤害 {damage:.2f}")
            self.take_damage(damage, logger, "混乱误伤")
            self._gain_shield(logger)
            return
        super().perform_basic_attack(opponent, logger)
        self._gain_shield(logger)
