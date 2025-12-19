import os
from deploy.utils.logger import log_info, log_error
from core.port_scanner import PortScanner
from core.config_model import ConfigModel


class InstanceCreator:
    """
    实例目录创建器：
    - 创建实例目录结构
    - 自动生成 config.json（调用 ConfigModel）
    """

    # -----------------------------------------------
    # 创建目录结构
    # -----------------------------------------------
    @staticmethod
    def create_structure(base_path: str, name: str) -> str:
        """
        创建实例的完整目录结构
        base_path: /opt/mc-instances
        name: 实例名（已通过 InstanceNamer 处理）
        """

        instance_dir = os.path.join(base_path, name)

        # 如果已经存在，极小概率（理论上由 namer 避免）
        if os.path.exists(instance_dir):
            log_error(f"实例目录已存在：{instance_dir}")
            raise RuntimeError("目录已存在异常")

        # 创建主要目录
        subdirs = ["data", "logs", "backups", "panel"]
        os.makedirs(instance_dir, exist_ok=False)

        for d in subdirs:
            os.makedirs(os.path.join(instance_dir, d), exist_ok=True)

        log_info(f"实例目录已创建：{instance_dir}")
        return instance_dir

    # -----------------------------------------------
    # 自动生成 config.json
    # -----------------------------------------------
    @staticmethod
    def generate_config(instance_dir: str, instance_name: str):
        """
        自动分配端口，并写入 config.json
        """

        # 自动寻找可用端口
        mc_port = PortScanner.find_free(25565)
        panel_port = PortScanner.find_free(15000)

        log_info(f"分配到 MC 端口：{mc_port}")
        log_info(f"分配到面板端口：{panel_port}")

        config_path = os.path.join(instance_dir, "config.json")

        cfg = ConfigModel.create(
            path=config_path,
            instance_name=instance_name,
            instance_dir=instance_dir,
            mc_port=mc_port,
            panel_port=panel_port
        )

        return cfg

    # -----------------------------------------------
    # 综合入口（供 setup.py 调用）
    # -----------------------------------------------
    @staticmethod
    def create_instance(base_path: str, name: str):
        """
        创建实例目录 + 写 config.json
        返回：(instance_dir, ConfigModel 对象)
        """

        instance_dir = InstanceCreator.create_structure(base_path, name)
        cfg = InstanceCreator.generate_config(instance_dir, name)
        return instance_dir, cfg