"""角色定义."""

from __future__ import annotations

from ...logger import BattleLogger
from ...stats import CombatStats
from ..base import BaseCharacter


class Lita(BaseCharacter):
    """丽塔: 高速削甲并反击的刺客."""

    def __init__(self) -> None:
        super().__init__(
            name="丽塔",
            stats=CombatStats(max_hp=100.0, attack=22.0, defense=9.0, speed=25.0),
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
        damage = self.calculate_skill_damage(15.0, opponent)
        self.log_action(logger, "active", f"发动削甲迅袭, 造成 {damage:.2f} 并降低对方防御")
        opponent.take_damage(damage, logger, "主动技能", attacker=self)
        current = opponent.states.get("减防", {"剩余回合": 0, "减防": 0.0})
        current["剩余回合"] = 2
        current["减防"] = current.get("减防", 0.0) + 3.0
        opponent.apply_state("减防", current, logger)
        return True

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
        # 被动判定“主动攻击”：只要不是状态/治疗/被动来源的直接伤害(含普攻)，都视为可闪避对象.
        is_direct_attack = category not in {"state", "heal", "passive"}
        if (
            is_direct_attack
            and attacker
            and not self.is_passive_blocked()
            and self.roll_chance(0.18)
        ):
            self.log_action(logger, "passive", "成功闪避并反击 12 点伤害")
            attacker.take_damage(
                12.0,
                logger,
                "被动:闪避反击",
                ignore_shield=False,
                attacker=self,
            )
            return
        super().take_damage(
            amount,
            logger,
            source,
            ignore_shield=ignore_shield,
            attacker=attacker,
        )
