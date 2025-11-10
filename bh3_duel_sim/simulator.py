"""战斗模拟模块."""

from __future__ import annotations

import random
from typing import Callable, Dict, List, Tuple

from bh3_duel_sim.characters.base import BaseCharacter
from bh3_duel_sim.logger import BattleLogger


class BattleSimulator:
    """战斗驱动器."""

    def __init__(self, seed: int = 2024) -> None:
        self.rng = random.Random(seed)

    def simulate_once(
        self,
        fighter_a: BaseCharacter,
        fighter_b: BaseCharacter,
        logger: BattleLogger,
    ) -> BaseCharacter:
        """执行一场对局."""
        fighter_a.reset_for_battle()
        fighter_b.reset_for_battle()
        logger.log(f"=== 对局开始: {fighter_a.name} vs {fighter_b.name} ===")
        order = self._decide_order(fighter_a, fighter_b)
        round_count = 1
        while fighter_a.is_alive and fighter_b.is_alive:
            logger.log(f"-- 第 {round_count} 回合 --")
            for actor, target in order:
                if not (actor.is_alive and target.is_alive):
                    break
                self._exec_turn(actor, target, logger)
            round_count += 1
        winner = fighter_a if fighter_a.is_alive else fighter_b
        logger.log(f"=== 胜者: {winner.name} ===")
        return winner

    def _decide_order(
        self, fighter_a: BaseCharacter, fighter_b: BaseCharacter
    ) -> List[Tuple[BaseCharacter, BaseCharacter]]:
        """根据速度决定先后手,速度相同时随机."""
        if fighter_a.stats.speed > fighter_b.stats.speed:
            return [(fighter_a, fighter_b), (fighter_b, fighter_a)]
        if fighter_b.stats.speed > fighter_a.stats.speed:
            return [(fighter_b, fighter_a), (fighter_a, fighter_b)]
        if self.rng.random() < 0.5:
            return [(fighter_a, fighter_b), (fighter_b, fighter_a)]
        return [(fighter_b, fighter_a), (fighter_a, fighter_b)]

    def _exec_turn(
        self, actor: BaseCharacter, target: BaseCharacter, logger: BattleLogger
    ) -> None:
        """执行单个角色的行动阶段."""
        actor.apply_state_effects(target, logger)
        if not actor.is_alive:
            return
        if not target.is_alive:
            return

        passive_consumed_action = actor.trigger_passive(target, logger)
        if not actor.is_alive or not target.is_alive:
            return
        if passive_consumed_action:
            return

        if actor.use_active_skill(target, logger):
            return

        actor.perform_basic_attack(target, logger)


def mass_battle_statistics(
    simulator: BattleSimulator,
    spawn_a: Callable[[], BaseCharacter],
    spawn_b: Callable[[], BaseCharacter],
    iterations: int = 10_000,
) -> Dict[str, float]:
    """重复模拟多场对局并统计胜率."""
    sample_a = spawn_a()
    sample_b = spawn_b()
    name_a = sample_a.name
    name_b = sample_b.name
    del sample_a
    del sample_b
    wins: Dict[str, int] = {name_a: 0, name_b: 0}
    quiet_logger = BattleLogger(enabled=False)
    for _ in range(iterations):
        winner = simulator.simulate_once(spawn_a(), spawn_b(), quiet_logger)
        wins[winner.name] = wins.get(winner.name, 0) + 1
    return {name: count / iterations for name, count in wins.items()}


def run_single_verbose_battle(
    simulator: BattleSimulator,
    spawn_a: Callable[[], BaseCharacter],
    spawn_b: Callable[[], BaseCharacter],
) -> None:
    """输出一场带日志的对局."""
    logger = BattleLogger(enabled=True)
    simulator.simulate_once(spawn_a(), spawn_b(), logger)
