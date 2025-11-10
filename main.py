"""项目入口."""

from __future__ import annotations

from bh3_duel_sim.characters.placeholder import build_placeholder_fighters
from bh3_duel_sim.simulator import BattleSimulator, mass_battle_statistics, run_single_verbose_battle


def main() -> None:
    """主流程: 先跑 1 万次统计胜率,再输出一场日志."""
    simulator = BattleSimulator()
    spawn_a, spawn_b = build_placeholder_fighters()
    stats = mass_battle_statistics(simulator, spawn_a, spawn_b)
    for name, rate in stats.items():
        print(f"{name} 胜率: {rate:.2%}")
    print("\n示例对局日志:")
    run_single_verbose_battle(simulator, spawn_a, spawn_b)


if __name__ == "__main__":
    main()
