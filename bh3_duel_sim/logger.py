"""战斗日志模块."""

from __future__ import annotations


class BattleLogger:
    """简单开关式日志器."""

    def __init__(self, enabled: bool) -> None:
        self.enabled = enabled

    def log(self, message: str) -> None:
        """仅在开启时输出日志."""
        if self.enabled:
            print(message)
