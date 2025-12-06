import os
from utils.logger import log_info, log_warn


class InstanceNamer:
    """
    实例命名系统：
    - 用户可自定义名称
    - 留空自动生成 instance-XXX
    - 检查并处理名称冲突
    """

    @staticmethod
    def sanitize(name: str) -> str:
        """清洗实例名：只允许 a-z 0-9 - _"""
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
        """如果名字冲突，则在后面自动加序号"""
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
    def ask_name(base_path: str) -> str:
        """
        询问用户实例名：
        - 留空 → 自动生成 ID
        - 自定义 → 清洗 + 冲突检查
        """

        print()
        user_input = input("请输入实例名称（留空自动生成）： ").strip()

        # 自动生成
        if user_input == "":
            name = InstanceNamer.auto_generate(base_path)
            log_info(f"已自动生成实例名：{name}")
            return name

        # 用户自定义（清洗）
        clean = InstanceNamer.sanitize(user_input)

        # 避免生成透明空值，例如全是非法字符
        if clean == "":
            log_warn("输入的名称无有效字符，将自动生成实例ID。")
            return InstanceNamer.auto_generate(base_path)

        # 冲突处理
        final = InstanceNamer.handle_conflict(base_path, clean)

        log_info(f"实例名确定为：{final}")
        return final