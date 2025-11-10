## 风格与约定
- 编码风格：明确要求模仿 Linus Torvalds——实现要直白、精简、可维护，拒绝过度抽象；设计保持高内聚/低耦合，所有共性逻辑（例如状态、冷却）集中在 `BaseCharacter`。
- 文本/日志：全程使用中文；每个类与公开函数必须写中文 docstring，复杂片段再加行内注释。
- 代码规范：Python 使用 4 空格缩进、`PascalCase` 类名、`snake_case` 函数与变量名；模块导入优先包内相对写法（例如 `from .base import BaseCharacter`）。
- 状态/技能机制：必须复用基类的 `process_state`、`configure_active_cooldown`、`consume_active_charge` 等工具，避免在子类重复实现，保证状态“先生效后减回合”。
- 输出：战斗日志需要在角色类内部细化（父类只保留通用打印），生命变化必须即时打印当前值。