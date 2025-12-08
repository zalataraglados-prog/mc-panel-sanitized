import os
import sys
from utils.logger import log_info, log_warn


class InstanceNamer:
    """实例命名辅助工具。"""

    @staticmethod
    def sanitize(name: str) -> str:
        """规范实例名称：只允许 a-z、0-9、-、_。"""
        safe = []
        for c in name.lower():
            if c.isalnum() or c in "-_":
                safe.append(c)
            else:
                safe.append("-")
        return "".join(safe)

    @staticmethod
    def auto_generate(base_path: str) -> str:
        """自动生成 instance-001 / instance-002 / ..."""

        n = 1
        while True:
            candidate = f"instance-{n:03d}"
            full_path = os.path.join(base_path, candidate)
            if not os.path.exists(full_path):
                return candidate
            n += 1

    @staticmethod
    def handle_conflict(base_path: str, name: str) -> str:
        """如果实例名已存在，则自动附加数字后缀避免冲突。"""
        if not os.path.exists(os.path.join(base_path, name)):
            return name

        log_warn(f"实例名 '{name}' 已存在，将自动附加序号避免冲突。")

        n = 2
        while True:
            new_name = f"{name}-{n}"
            full_path = os.path.join(base_path, new_name)
            if not os.path.exists(full_path):
                return new_name
            n += 1

    @staticmethod
    def _read_input(prompt: str) -> str:
        """读取用户输入；优先使用交互式 stdin，无则回退到终端设备。"""

        # 常规交互输入
        if sys.stdin and sys.stdin.isatty():
            try:
                return input(prompt)
            except EOFError:
                return ""

        # 非交互式环境下使用终端设备
        tty_path = "CON" if os.name == "nt" else "/dev/tty"
        try:
            with open(tty_path, "r") as tty:
                print(prompt, end="", flush=True)
                return tty.readline()
        except Exception:
            log_warn("无法读取用户输入，将自动生成实例名称。")
            return ""

    @staticmethod
    def ask_name(base_path: str) -> str:
        """
        询问用户实例名：
        - 空输入 → 自动生成
        - 自定义 → 清洗后检查冲突
        """

        print()
        user_input = InstanceNamer._read_input("请输入实例名称（留空自动生成）： ").strip()

        if user_input == "":
            log_info("未检测到用户输入，将自动生成实例名称。")
            name = InstanceNamer.auto_generate(base_path)
            log_info(f"自动生成的实例名称为：{name}")
            return name

        clean = InstanceNamer.sanitize(user_input)

        if clean == "":
            log_warn("输入中无有效字符，将自动生成实例名称。")
            return InstanceNamer.auto_generate(base_path)

        final = InstanceNamer.handle_conflict(base_path, clean)

        log_info(f"实例名称已确定：{final}")
        return final
