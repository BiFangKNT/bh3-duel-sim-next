"""角色基类定义."""

from __future__ import annotations

import random
from typing import Dict, Optional

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
        self._rng: Optional[random.Random] = None

    def bind_rng(self, rng: random.Random) -> None:
        """在战斗开始时由驱动绑定随机源."""
        self._rng = rng

    def _require_rng(self) -> random.Random:
        if self._rng is None:
            raise RuntimeError("未绑定随机源")
        return self._rng

    def roll_chance(self, probability: float) -> bool:
        """根据绑定随机源判定概率事件."""
        if not 0.0 <= probability <= 1.0:
            raise ValueError("概率需要位于[0, 1]")
        return self._require_rng().random() < probability

    def calculate_skill_damage(self, base_damage: float, opponent: "BaseCharacter") -> float:
        """技能伤害通用处理: 伤害值也需受防御影响."""
        raw = max(0.0, base_damage)
        mitigated = max(0.0, raw - opponent.effective_defense())
        floor = raw * 0.05  # 最低伤害,防止被完全抵消
        return max(mitigated, floor)

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

    def take_damage(
        self,
        amount: float,
        logger: BattleLogger,
        source: str,
        *,
        ignore_shield: bool = False,
    ) -> None:
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
