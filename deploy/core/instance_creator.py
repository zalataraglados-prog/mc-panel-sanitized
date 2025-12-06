import os
from datetime import datetime
from utils.logger import log_info, log_error
from utils.file_helper import FileHelper
from core.port_scanner import PortScanner
from core.config_model import ConfigModel


class InstanceCreator:
    """
    创建实例目录 + 使用模板生成 config.json
    """

    def __init__(self, templates_dir="templates", deployer_version="0.1.0"):
        self.templates_dir = templates_dir
        self.deployer_version = deployer_version

    # --------------------------------------------------------------
    # 创建目录结构
    # --------------------------------------------------------------
    @staticmethod
    def create_structure(base_path: str, name: str) -> str:
        instance_dir = os.path.join(base_path, name)

        if os.path.exists(instance_dir):
            log_error(f"实例目录已存在：{instance_dir}")
            raise RuntimeError("实例目录已存在")

        subdirs = ["data", "logs", "backups", "panel"]
        os.makedirs(instance_dir, exist_ok=True)

        for d in subdirs:
            os.makedirs(os.path.join(instance_dir, d), exist_ok=True)

        log_info(f"实例目录已创建：{instance_dir}")
        return instance_dir

    # --------------------------------------------------------------
    # 模板渲染 config.json
    # --------------------------------------------------------------
    def generate_config(self, instance_dir: str, instance_name: str):
        tpl_path = os.path.join(self.templates_dir, "config.json.tpl")

        if not os.path.exists(tpl_path):
            log_error(f"找不到模板文件：{tpl_path}")
            raise FileNotFoundError(tpl_path)

        template = FileHelper.load_file(tpl_path)

        # 自动端口分配
        mc_port = PortScanner.find_free(25565)
        panel_port = PortScanner.find_free(15000)
        rcon_port = mc_port + 10

        created_at = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        vars = {
            "INSTANCE_NAME": instance_name,
            "INSTANCE_DIR": instance_dir,

            "MC_PORT": mc_port,
            "PANEL_PORT": panel_port,
            "RCON_PORT": rcon_port,

            "MC_VERSION": "1.16.5",
            "MC_MEMORY": "4G",

            "CREATED_AT": created_at,
            "DEPLOYER_VERSION": self.deployer_version,
            "RCON_PASSWORD": "changeme"
        }

        output = FileHelper.render_template(template, vars)

        config_path = os.path.join(instance_dir, "config.json")
        FileHelper.write_file(config_path, output)

        log_info(f"config.json 已生成：{config_path}")

        cfg = ConfigModel(config_path)
        cfg.load()
        return cfg

    # --------------------------------------------------------------
    # 主入口：供 setup.py 使用
    # --------------------------------------------------------------
    def create_instance(self, base_path: str, name: str):
        instance_dir = self.create_structure(base_path, name)
        cfg = self.generate_config(instance_dir, name)
        return instance_dir, cfg