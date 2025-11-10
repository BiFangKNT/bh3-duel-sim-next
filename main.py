"""项目入口."""

from __future__ import annotations

from bh3_duel_sim.characters.valkyries import build_valkyrie_roster
from bh3_duel_sim.simulator import (
    BattleSimulator,
    round_robin_statistics,
    run_single_verbose_battle,
)


def main() -> None:
    """主流程: 每个对阵 1 万场循环赛, 再输出一场示例战斗日志."""
    simulator = BattleSimulator()
    roster = build_valkyrie_roster()
    roster = {name: roster[name] for name in ("科拉莉", "布洛妮娅")}
    overall, matchup = round_robin_statistics(simulator, roster, iterations_per_pair=10_000)
    print("整体胜率(每个对手 1 万场):")
    for name, rate in overall.items():
        print(f"- {name}: {rate:.2%}")

    print("\n对阵详情:")
    for (attacker, defender), result in matchup.items():
        print(
            f"- {attacker} vs {defender}: "
            f"{attacker} {result[attacker]:.2%} / {defender} {result[defender]:.2%}"
        )

    names = list(roster.keys())
    if len(names) >= 2:
        print("\n示例对局日志:")
        run_single_verbose_battle(simulator, roster[names[0]], roster[names[1]])


if __name__ == "__main__":
    main()
