"""正式角色实现."""

from __future__ import annotations

from typing import Callable

from ..logger import BattleLogger
from ..stats import CombatStats
from .base import BaseCharacter


class Korali(BaseCharacter):
    """科拉莉: 连段输出 + 眩晕控制."""

    def __init__(self) -> None:
        super().__init__(
            name="科拉莉",
            stats=CombatStats(max_hp=100.0, attack=17.0, defense=6.0, speed=21.0),
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
        self._handle_bleed(logger)
        self._handle_stun(logger)
        self._handle_confusion(logger)

    def _handle_bleed(self, logger: BattleLogger) -> None:
        def effect(state: dict[str, float], remaining: int) -> None:
            logger.log(
                f"{self.name} 受到状态:流血 影响, 持续伤害 {state['伤害']:.2f} "
                f"(剩余 {remaining} 回合)"
            )
            self.take_damage(state["伤害"], logger, "状态:流血")

        self.process_state("流血", logger, effect, end_message=f"{self.name} 的流血状态结束")

    def _handle_stun(self, logger: BattleLogger) -> None:
        def effect(_: dict[str, float], remaining: int) -> None:
            self._stunned = True
            logger.log(f"{self.name} 陷入眩晕, 本回合无法发动主动或普攻 (剩余 {remaining} 回合)")

        self.process_state("眩晕", logger, effect, end_message=f"{self.name} 的眩晕状态结束")

    def _handle_confusion(self, logger: BattleLogger) -> None:
        def effect(_: dict[str, float], remaining: int) -> None:
            self._confused = True
            logger.log(f"{self.name} 陷入混乱, 普攻会转而攻击自己 (剩余 {remaining} 回合)")

        self.process_state("混乱", logger, effect, end_message=f"{self.name} 的混乱状态结束")

    def trigger_passive(self, opponent: BaseCharacter, logger: BattleLogger) -> bool:
        if self._stunned:
            logger.log(f"{self.name} 因眩晕跳过本回合的主动与普攻")
            return True
        return False

    def _try_apply_stun(self, opponent: BaseCharacter, logger: BattleLogger) -> None:
        if not opponent.is_alive:
            return
        if self.roll_chance(0.20):
            opponent.states["眩晕"] = {"剩余回合": 2}
            logger.log(f"{self.name} 的被动生效, {opponent.name} 进入 2 回合眩晕")

    def use_active_skill(self, opponent: BaseCharacter, logger: BattleLogger) -> bool:
        if not self.consume_active_charge():
            return False
        logger.log(f"{self.name} 释放主动技能, 进行三段斩击")
        segments = [20.0, 18.0, 18.0]
        for idx, base in enumerate(segments, start=1):
            damage = self.calculate_skill_damage(base, opponent)
            # 每段独立结算防御/护盾,避免未来遗忘该设定.
            logger.log(f"{self.name} 主动技能第 {idx} 段预期伤害 {damage:.2f} (独立结算防御/护盾)")
            opponent.take_damage(damage, logger, "主动技能")
            if not opponent.is_alive:
                break
        if opponent.is_alive:
            self._try_apply_stun(opponent, logger)
        return True

    def perform_basic_attack(self, opponent: BaseCharacter, logger: BattleLogger) -> None:
        if self._confused:
            damage = max(
                0.05 * self.effective_attack(),
                self.effective_attack() - self.effective_defense(),
            )
            logger.log(f"{self.name} 因混乱攻击自己, 预计伤害 {damage:.2f}")
            self.take_damage(damage, logger, "混乱误伤")
            return
        super().perform_basic_attack(opponent, logger)
        if opponent.is_alive:
            self._try_apply_stun(opponent, logger)


class Bronya(BaseCharacter):
    """布洛妮娅: 多段炮火与混乱控制."""

    def __init__(self) -> None:
        super().__init__(
            name="布洛妮娅",
            stats=CombatStats(max_hp=100.0, attack=18.0, defense=6.0, speed=20.0),
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
        self._handle_bleed(logger)
        self._handle_stun(logger)
        self._handle_confusion(logger)

    def _handle_bleed(self, logger: BattleLogger) -> None:
        def effect(state: dict[str, float], remaining: int) -> None:
            logger.log(
                f"{self.name} 受到状态:流血 影响, 持续伤害 {state['伤害']:.2f} "
                f"(剩余 {remaining} 回合)"
            )
            self.take_damage(state["伤害"], logger, "状态:流血")

        self.process_state("流血", logger, effect, end_message=f"{self.name} 的流血状态结束")

    def _handle_stun(self, logger: BattleLogger) -> None:
        def effect(_: dict[str, float], remaining: int) -> None:
            self._stunned = True
            logger.log(f"{self.name} 陷入眩晕, 本回合无法发动主动或普攻 (剩余 {remaining} 回合)")

        self.process_state("眩晕", logger, effect, end_message=f"{self.name} 的眩晕状态结束")

    def _handle_confusion(self, logger: BattleLogger) -> None:
        def effect(_: dict[str, float], remaining: int) -> None:
            self._confused = True
            logger.log(f"{self.name} 陷入混乱, 普攻会转而攻击自己 (剩余 {remaining} 回合)")

        self.process_state("混乱", logger, effect, end_message=f"{self.name} 的混乱状态结束")

    def trigger_passive(self, opponent: BaseCharacter, logger: BattleLogger) -> bool:
        if self._stunned:
            logger.log(f"{self.name} 因眩晕跳过本回合的主动与普攻")
            return True
        return False

    def use_active_skill(self, opponent: BaseCharacter, logger: BattleLogger) -> bool:
        if not self.consume_active_charge():
            return False
        logger.log(f"{self.name} 释放主动技能, 发射五段炮火")
        for idx in range(1, 6):
            if self.roll_chance(0.15):
                logger.log(f"第 {idx} 段触发被动, 无视防御与护盾")
                opponent.take_damage(15.0, logger, "主动技能", ignore_shield=True)
            else:
                damage = self.calculate_skill_damage(15.0, opponent)
                logger.log(f"第 {idx} 段预期伤害 {damage:.2f}")
                opponent.take_damage(damage, logger, "主动技能")
            if not opponent.is_alive:
                break
        if opponent.is_alive and self.roll_chance(0.25):
            opponent.states["混乱"] = {"剩余回合": 1}
            logger.log(f"{self.name} 触发混乱, {opponent.name} 将自伤 1 回合")
        return False

    def perform_basic_attack(self, opponent: BaseCharacter, logger: BattleLogger) -> None:
        if self._confused:
            damage = max(
                0.05 * self.effective_attack(),
                self.effective_attack() - self.effective_defense(),
            )
            logger.log(f"{self.name} 因混乱攻击自己, 预计伤害 {damage:.2f}")
            self.take_damage(damage, logger, "混乱误伤")
            return
        super().perform_basic_attack(opponent, logger)


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

    def _handle_bleed(self, logger: BattleLogger) -> None:
        def effect(state: dict[str, float], remaining: int) -> None:
            logger.log(
                f"{self.name} 受到状态:流血 影响, 持续伤害 {state['伤害']:.2f} "
                f"(剩余 {remaining} 回合)"
            )
            self.take_damage(state["伤害"], logger, "状态:流血")

        self.process_state("流血", logger, effect, end_message=f"{self.name} 的流血状态结束")

    def _handle_stun(self, logger: BattleLogger) -> None:
        def effect(_: dict[str, float], remaining: int) -> None:
            self._stunned = True
            logger.log(f"{self.name} 陷入眩晕, 本回合无法发动主动或普攻 (剩余 {remaining} 回合)")

        self.process_state("眩晕", logger, effect, end_message=f"{self.name} 的眩晕状态结束")

    def _handle_confusion(self, logger: BattleLogger) -> None:
        def effect(_: dict[str, float], remaining: int) -> None:
            self._confused = True
            logger.log(f"{self.name} 陷入混乱, 普攻会转而攻击自己 (剩余 {remaining} 回合)")

        self.process_state("混乱", logger, effect, end_message=f"{self.name} 的混乱状态结束")

    def trigger_passive(self, opponent: BaseCharacter, logger: BattleLogger) -> bool:
        if self._stunned:
            logger.log(f"{self.name} 因眩晕跳过本回合的主动与普攻")
            return True
        return False

    def _gain_shield(self, logger: BattleLogger) -> None:
        self._shield_value += 5.0
        logger.log(f"{self.name} 的被动生效, 获得 5 点护盾 -> 当前 {self._shield_value:.2f}")

    def _maybe_bonus_slash(self, opponent: BaseCharacter, logger: BattleLogger) -> None:
        if not opponent.is_alive:
            return
        if self.roll_chance(0.20):
            damage = self.calculate_skill_damage(24.0, opponent)
            logger.log(f"{self.name} 的主动追加斩击触发, 额外造成 {damage:.2f} (不计入被动)")
            opponent.take_damage(damage, logger, "主动技能追加")

    def use_active_skill(self, opponent: BaseCharacter, logger: BattleLogger) -> bool:
        if not self.consume_active_charge():
            return False
        damage = self.calculate_skill_damage(16.0, opponent)
        logger.log(f"{self.name} 以主动替换普攻, 造成 {damage:.2f} 伤害")
        opponent.take_damage(damage, logger, "主动技能")
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
    ) -> None:
        if not ignore_shield and self._shield_value > 0 and amount > 0:
            absorbed = min(amount, self._shield_value)
            self._shield_value -= absorbed
            logger.log(
                f"{self.name} 的护盾吸收 {absorbed:.2f} 点伤害 -> 剩余护盾 {self._shield_value:.2f}"
            )
            amount -= absorbed
        if amount <= 0:
            return
        super().take_damage(amount, logger, source, ignore_shield=ignore_shield)

    def perform_basic_attack(self, opponent: BaseCharacter, logger: BattleLogger) -> None:
        if self._confused:
            damage = max(
                0.05 * self.effective_attack(),
                self.effective_attack() - self.effective_defense(),
            )
            logger.log(f"{self.name} 因混乱攻击自己, 预计伤害 {damage:.2f}")
            self.take_damage(damage, logger, "混乱误伤")
            self._gain_shield(logger)
            return
        super().perform_basic_attack(opponent, logger)
        self._gain_shield(logger)


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

    def _handle_bleed(self, logger: BattleLogger) -> None:
        def effect(state: dict[str, float], remaining: int) -> None:
            logger.log(
                f"{self.name} 受到状态:流血 影响, 持续伤害 {state['伤害']:.2f} "
                f"(剩余 {remaining} 回合)"
            )
            self.take_damage(state["伤害"], logger, "状态:流血")

        self.process_state("流血", logger, effect, end_message=f"{self.name} 的流血状态结束")

    def _handle_stun(self, logger: BattleLogger) -> None:
        def effect(_: dict[str, float], remaining: int) -> None:
            self._stunned = True
            logger.log(f"{self.name} 陷入眩晕, 本回合无法发动主动或普攻 (剩余 {remaining} 回合)")

        self.process_state("眩晕", logger, effect, end_message=f"{self.name} 的眩晕状态结束")

    def _handle_confusion(self, logger: BattleLogger) -> None:
        def effect(_: dict[str, float], remaining: int) -> None:
            self._confused = True
            logger.log(f"{self.name} 陷入混乱, 普攻会转而攻击自己 (剩余 {remaining} 回合)")

        self.process_state("混乱", logger, effect, end_message=f"{self.name} 的混乱状态结束")

    def trigger_passive(self, opponent: BaseCharacter, logger: BattleLogger) -> bool:
        if self._stunned:
            logger.log(f"{self.name} 因眩晕跳过本回合的主动与普攻")
            return True
        return False

    def use_active_skill(self, opponent: BaseCharacter, logger: BattleLogger) -> bool:
        if not self.consume_active_charge():
            return False
        if opponent.is_alive:
            bonus = max(1.0, opponent.current_hp * 0.15)
            logger.log(f"{self.name} 被动发动, 先造成 {bonus:.2f} 点真实伤害")
            opponent.take_damage(bonus, logger, "被动:超限打击", ignore_shield=True)
        if opponent.is_alive:
            damage = self.calculate_skill_damage(20.0, opponent)
            logger.log(f"{self.name} 主动追加 20 点伤害, 预期 {damage:.2f}")
            opponent.take_damage(damage, logger, "主动技能")
        return False

    def perform_basic_attack(self, opponent: BaseCharacter, logger: BattleLogger) -> None:
        if self._confused:
            damage = max(
                0.05 * self.effective_attack(),
                self.effective_attack() - self.effective_defense(),
            )
            logger.log(f"{self.name} 因混乱攻击自己, 预计伤害 {damage:.2f}")
            self.take_damage(damage, logger, "混乱误伤")
            return
        super().perform_basic_attack(opponent, logger)


def build_valkyrie_roster() -> dict[str, Callable[[], BaseCharacter]]:
    """提供默认四人角色工厂."""
    return {
        "科拉莉": Korali,
        "布洛妮娅": Bronya,
        "比安卡": Bianka,
        "琪亚娜": Kiana,
    }
