## 常用命令
- `python3 main.py`：运行 1 万场循环赛并输出一场示例对局日志，最基本的本地回归。
- `uv run pyright`：在 uv 虚拟环境中执行 Pyright 静态检查，捕捉导入与类型错误。
- `uv add <package>` / `uv remove <package>`：添加或移除 Python 依赖（会同步更新 `pyproject.toml` 与 `uv.lock`）。
- `uv run python -m pytest`（若未来添加 tests/）：以 uv 环境执行 pytest 测试套件。
- 常规 Linux/uv 工具：`ls`, `rg`, `git status`, `git diff` 等用于查看文件与版本状态。