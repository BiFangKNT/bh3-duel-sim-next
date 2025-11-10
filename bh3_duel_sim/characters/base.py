"""角色基类定义."""

from __future__ import annotations

from typing import Dict

from bh3_duel_sim.logger import BattleLogger
from bh3_duel_sim.stats import CombatStats


class BaseCharacter:
    """角色基类,仅保留通用的数值和基础日志."""

    def __init__(self, name: str, stats: CombatStats) -> None:
        self.name = name
        self.stats = stats
        self.current_hp = stats.max_hp
        self.states: Dict[str, Dict[str, float]] = {}
        self.bonus_attack = 0.0
        self.bonus_defense = 0.0

    def reset_for_battle(self) -> None:
        """恢复满血并清空状态."""
        self.current_hp = self.stats.max_hp
        self.states.clear()
        self.bonus_attack = 0.0
        self.bonus_defense = 0.0

    @property
    def is_alive(self) -> bool:
        """判断角色是否存活."""
        return self.current_hp > 0

    def effective_attack(self) -> float:
        """计算当前攻击力."""
        return max(0.0, self.stats.attack + self.bonus_attack)

    def effective_defense(self) -> float:
        """计算当前防御力."""
        return max(0.0, self.stats.defense + self.bonus_defense)

    def take_damage(self, amount: float, logger: BattleLogger, source: str) -> None:
        """承受伤害并打印剩余生命."""
        damage = max(0.0, amount)
        self.current_hp = max(0.0, self.current_hp - damage)
        logger.log(
            f"{self.name} 受到{source} {damage:.2f} 点伤害 -> "
            f"生命 {self.current_hp:.2f}/{self.stats.max_hp:.2f}"
        )

    def heal(self, amount: float, logger: BattleLogger, source: str) -> None:
        """获得治疗并打印剩余生命."""
        heal_value = max(0.0, amount)
        self.current_hp = min(self.stats.max_hp, self.current_hp + heal_value)
        logger.log(
            f"{self.name} 获得{source} {heal_value:.2f} 点治疗 -> "
            f"生命 {self.current_hp:.2f}/{self.stats.max_hp:.2f}"
        )

    def perform_basic_attack(self, opponent: "BaseCharacter", logger: BattleLogger) -> None:
        """默认普攻,按攻防差造成伤害."""
        raw = max(0.05 * self.effective_attack(), self.effective_attack() - opponent.effective_defense())
        logger.log(f"{self.name} 进行普攻, 预期伤害 {raw:.2f}")
        opponent.take_damage(raw, logger, "普攻")

    def apply_state_effects(self, opponent: "BaseCharacter", logger: BattleLogger) -> None:
        """状态阶段,需要由子类实现."""
        raise NotImplementedError

    def trigger_passive(self, opponent: "BaseCharacter", logger: BattleLogger) -> bool:
        """被动阶段,返回 True 表示已经完成一次进攻动作."""
        raise NotImplementedError

    def use_active_skill(self, opponent: "BaseCharacter", logger: BattleLogger) -> bool:
        """主动技能阶段,返回 True 表示技能已经释放."""
        raise NotImplementedError
