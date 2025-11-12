"""角色定义."""

from __future__ import annotations

from ...logger import BattleLogger
from ...stats import CombatStats
from ..base import ATTRIBUTE_DEBUFF_STATES, CONTROL_STATES, BaseCharacter


class Theresa(BaseCharacter):
    """德丽莎: 抵御控制即回复, 攻击封锁对手被动."""

    NEGATIVE_STATE_NAMES = ATTRIBUTE_DEBUFF_STATES | CONTROL_STATES
    PASSIVE_MARK_KEY = "theresa_passive_mark"

    def __init__(self) -> None:
        super().__init__(
            name="德丽莎",
            stats=CombatStats(max_hp=100.0, attack=23.0, defense=7.0, speed=24.0),
        )
        self.configure_active_cooldown(3)
        self._stunned = False
        self._confused = False

    def reset_for_battle(self) -> None:
        super().reset_for_battle()
        self._stunned = False
        self._confused = False

    def apply_state_effects(self, opponent: BaseCharacter, logger: BattleLogger) -> None:
        self._stunned = False
        self._confused = False
        self._trigger_sanctified_blood(logger)
        self._handle_bleed(logger)
        self._handle_stun(logger)
        self._handle_confusion(logger)
        self._handle_defense_break(logger)

    def _trigger_sanctified_blood(self, logger: BattleLogger) -> None:
        for state_name in list(self.states.keys()):
            if state_name not in self.NEGATIVE_STATE_NAMES:
                continue
            self._try_sanctified_heal(state_name, logger)

    def _try_sanctified_heal(self, state_name: str, logger: BattleLogger) -> None:
        state = self.states.get(state_name)
        if not state:
            return
        if self.is_passive_blocked():
            return
        if state.get(self.PASSIVE_MARK_KEY):
            return
        state[self.PASSIVE_MARK_KEY] = 1.0
        heal_value = max(0.0, self.max_hp * 0.10)
        self.heal(heal_value, logger, "被动:圣血赐福")

    def on_state_inflicted(self, state_name: str, logger: BattleLogger) -> None:
        super().on_state_inflicted(state_name, logger)
        if state_name in self.NEGATIVE_STATE_NAMES:
            self._try_sanctified_heal(state_name, logger)

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
        self.log_action(logger, "active", "发动圣血祷言, 本回合以主动替换普攻")
        if self.roll_chance(0.70):
            damage = self.calculate_skill_damage(30.0, opponent)
            self.log_action(logger, "active", f"祷言命中, 造成 {damage:.2f} 点伤害")
            opponent.take_damage(damage, logger, "主动技能", attacker=self)
        else:
            self.log_action(
                logger,
                "active",
                "祷言失误, 仅造成 1 点真实伤害并回复 18 点生命",
            )
            opponent.take_damage(1.0, logger, "主动技能", ignore_shield=True, attacker=self)
            self.heal(18.0, logger, "主动技能:圣血恢复")
        if opponent.is_alive:
            self._try_disable_opponent_passive(opponent, logger, "主动技能")
        return True

    def perform_basic_attack(self, opponent: BaseCharacter, logger: BattleLogger) -> None:
        if self._confused:
            damage = self.calculate_basic_damage(self)
            self.log_action(logger, "state", f"因混乱攻击自己, 预计伤害 {damage:.2f}")
            self.take_damage(damage, logger, "混乱误伤")
            return
        super().perform_basic_attack(opponent, logger)
        if opponent.is_alive:
            self._try_disable_opponent_passive(opponent, logger, "普攻")

    def _try_disable_opponent_passive(
        self, opponent: BaseCharacter, logger: BattleLogger, source: str
    ) -> None:
        if self.is_passive_blocked():
            return
        if not opponent.is_alive:
            return
        if not self.roll_chance(0.25):
            return
        opponent.apply_state("被动封锁", {"剩余回合": 2}, logger)
        logger.emit(opponent.name, "state", f"{self.name} 的{source}使被动失效 2 回合")
