"""角色定义."""

from __future__ import annotations

from ...logger import BattleLogger
from ...stats import CombatStats
from ..base import BaseCharacter


class Vita(BaseCharacter):
    """薇塔: 羽翼姿态强化, 被动魅惑与自救."""

    WING_ATTACK_BONUS = 7.0
    WING_DEFENSE_BONUS = 3.0
    CHARM_CHANCE = 0.20
    REVIVE_CHANCE = 0.15

    def __init__(self) -> None:
        super().__init__(
            name="薇塔",
            stats=CombatStats(max_hp=100.0, attack=20.0, defense=8.0, speed=25.0),
        )
        self.configure_active_cooldown(3)
        self._stunned = False
        self._confused = False
        self._wing_form_turns = 0

    def reset_for_battle(self) -> None:
        super().reset_for_battle()
        self._stunned = False
        self._confused = False
        self._wing_form_turns = 0

    def apply_state_effects(self, opponent: BaseCharacter, logger: BattleLogger) -> None:
        self._stunned = False
        self._confused = False
        self._decay_wing_form(logger)
        self._handle_bleed(logger)
        self._handle_stun(logger)
        self._handle_confusion(logger)
        self._handle_defense_break(logger)

    def _decay_wing_form(self, logger: BattleLogger) -> None:
        if self._wing_form_turns <= 0:
            return
        self._wing_form_turns -= 1
        if self._wing_form_turns == 0:
            self.log_action(logger, "state", "全知的羽翼状态结束")

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
        self._wing_form_turns = 1
        self.log_action(logger, "active", "展开全知的羽翼, 攻击+7/防御+3 持续 1 回合")
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

    def effective_attack(self) -> float:
        value = super().effective_attack()
        if self._wing_form_turns > 0:
            value += self.WING_ATTACK_BONUS
        return value

    def effective_defense(self) -> float:
        value = super().effective_defense()
        if self._wing_form_turns > 0:
            value += self.WING_DEFENSE_BONUS
        return value

    def take_damage(
        self,
        amount: float,
        logger: BattleLogger,
        source: str,
        *,
        ignore_shield: bool = False,
        attacker: BaseCharacter | None = None,
    ) -> None:
        category = logger.classify_source(source)
        super().take_damage(
            amount,
            logger,
            source,
            ignore_shield=ignore_shield,
            attacker=attacker,
        )
        if (
            attacker
            and attacker.is_alive
            and category not in {"state", "heal"}
            and not self.is_passive_blocked()
        ):
            self._try_apply_charm(attacker, logger)
        if self.current_hp <= 0 and not self.is_passive_blocked():
            self._try_revive(logger)

    def _try_apply_charm(self, attacker: BaseCharacter, logger: BattleLogger) -> None:
        if not self.roll_chance(self.CHARM_CHANCE):
            return
        attacker.apply_state("魅惑", {"剩余回合": 2}, logger)
        logger.emit(attacker.name, "state", f"{self.name} 的被动发动, 陷入 2 回合魅惑")

    def _try_revive(self, logger: BattleLogger) -> None:
        if not self.roll_chance(self.REVIVE_CHANCE):
            return
        self.current_hp = max(self.max_hp * 0.20, 1.0)
        self.log_action(
            logger,
            "passive",
            f"羽翼庇护发动, 复活并恢复至 {self.current_hp:.2f}/{self.max_hp:.2f}",
        )
