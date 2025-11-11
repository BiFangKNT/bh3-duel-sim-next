"""战斗日志模块."""

from __future__ import annotations

from collections.abc import Iterable


class BattleLogger:
    """支持颜色与类别区分的日志器."""

    RESET = "\033[0m"
    ACTOR_COLORS = ("\033[91m", "\033[94m")  # 红 / 蓝
    CATEGORY_COLORS = {
        "system": "\033[90m",
        "state": "\033[95m",
        "passive": "\033[96m",
        "active": "\033[93m",
        "basic": "\033[92m",
        "heal": "\033[92m",
        "damage": "\033[91m",
    }

    def __init__(self, enabled: bool) -> None:
        self.enabled = enabled
        self._actor_colors: dict[str, str] = {}

    def configure_actors(self, actors: Iterable[str]) -> None:
        """为参与者配置固定颜色."""
        self._actor_colors.clear()
        for color, name in zip(self.ACTOR_COLORS, actors):
            self._actor_colors[name] = color

    def _apply_color(self, text: str, color: str | None) -> str:
        if not color:
            return text
        return f"{color}{text}{self.RESET}"

    def log(self, message: str) -> None:
        """仅在开启时输出日志."""
        if self.enabled:
            print(message)

    def emit(self, actor_name: str | None, category: str, content: str) -> None:
        """输出带有角色颜色与分类颜色的日志."""
        if not self.enabled:
            return
        actor_segment = ""
        if actor_name:
            actor_segment = f"{self._apply_color(actor_name, self._actor_colors.get(actor_name))} "
        category_color = self.CATEGORY_COLORS.get(category)
        colored_content = self._apply_color(content, category_color)
        self.log(f"{actor_segment}{colored_content}")

    def log_system(self, content: str) -> None:
        """输出系统级日志."""
        self.emit(None, "system", content)

    @staticmethod
    def classify_source(source: str) -> str:
        """根据来源推断分类."""
        category = "damage"
        if source.startswith("状态"):
            category = "state"
        elif source.startswith("被动"):
            category = "passive"
        elif source.startswith("主动"):
            category = "active"
        elif source == "普攻":
            category = "basic"
        elif source == "混乱误伤":
            category = "state"
        elif source == "治疗":
            category = "heal"
        return category
