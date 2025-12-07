import json
import os
from datetime import datetime
from utils.logger import log_info, log_error
class ConfigModel:
    """
    核心配置模型：
    - 对应 config.json 的完整结构
    - 支持加载、保存、自动生成、字段访问
    """

    def __init__(self, path):
        self.path = path
        self.data = None  # 主配置字典

    # ----------------------------------------------------
    # 基础功能：加载与保存
    # ----------------------------------------------------

    def load(self):
        if not os.path.exists(self.path):
            log_error(f"Config 文件不存在：{self.path}")
            return False

        with open(self.path, "r") as f:
            self.data = json.load(f)

        return True

    def save(self):
        """将 self.data 写入 config.json"""
        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=4)

        log_info(f"Config 已保存：{self.path}")

    # ----------------------------------------------------
    # 自动生成默认配置
    # ----------------------------------------------------

    @staticmethod
    def generate_default(instance_name, instance_dir, mc_port, panel_port):
        """
        生成完整 config.json 的默认结构
        """

        now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        return {
            "schema_version": 1,

            "instance": {
                "name": instance_name,
                "display_name": instance_name,
                "description": "",
                "tags": [],
                "created_at": now,
                "updated_at": now,
                "enabled": True
            },

            "paths": {
                "instance_dir": instance_dir,
                "data_dir": os.path.join(instance_dir, "data"),
                "logs_dir": os.path.join(instance_dir, "logs"),
                "backups_dir": os.path.join(instance_dir, "backups"),
                "world_dir": os.path.join(instance_dir, "data/world"),
                "panel_dir": os.path.join(instance_dir, "panel")
            },

            "network": {
                "bind_address": "0.0.0.0",
                "host": "",
                "mc_port": mc_port,
                "panel_port": panel_port,
                "rcon_port": mc_port + 10,
                "query_port": mc_port,
                "use_https": False
            },

            "minecraft": {
                "engine": "paper",
                "version": "1.16.5",
                "world_name": "world",
                "difficulty": "hard",
                "game_mode": "survival",
                "max_players": 20,
                "online_mode": True,
                "view_distance": 10,
                "whitelist": False,
                "allow_flight": False,
                "level_type": "default",
                "motd": instance_name,

                "jvm": {
                    "memory": "4G",
                    "extra_args": "-XX:+UseG1GC"
                },

                "properties": {
                    "spawn-protection": 0,
                    "pvp": True
                }
            },

            "panel": {
                "enabled": True,
                "port": panel_port,
                "public_url": "",
                "secret_key": "",
                "auth_enabled": False
            },

            "docker": {
                "image": "itzg/minecraft-server",
                "tag": "java16",
                "restart_policy": "always",
                "networks": ["default"],
                "extra_env": {
                    "TZ": "Asia/Shanghai"
                },
                "volumes": {
                    "data": "./data:/data",
                    "logs": "./logs:/logs"
                }
            },

            "deployment": {
                "deployer_version": "0.1.0",
                "git_repo": "",
                "git_commit": "",
                "installed_by": "root",
                "installed_at": now,
                "auto_update": {
                    "enabled": False,
                    "channel": "stable"
                }
            },

            "security": {
                "rcon_enabled": True,
                "rcon_password": "changeme",
                "api_key": "",
                "allowed_ips": [],
                "allow_remote_panel": True
            },

            "features": {
                "enable_backups": False,
                "backup_cron": "0 4 * * *",
                "enable_metrics": False,
                "allow_offline_start": True,
                "auto_restart_on_crash": True
            }
        }

    # ----------------------------------------------------
    # 静态入口：创建并写入默认 config.json
    # ----------------------------------------------------

    @staticmethod
    def create(path, instance_name, instance_dir, mc_port, panel_port):
        cfg = ConfigModel(path)
        cfg.data = ConfigModel.generate_default(instance_name, instance_dir, mc_port, panel_port)
        cfg.save()
        return cfg

    # ----------------------------------------------------
    # 快捷访问属性
    # ----------------------------------------------------

    @property
    def instance_name(self):
        return self.data["instance"]["name"]

    @property
    def mc_port(self):
        return self.data["network"]["mc_port"]

    @property
    def panel_port(self):
        return self.data["network"]["panel_port"]

    @property
    def instance_dir(self):
        return self.data["paths"]["instance_dir"]
    
    # ----------------------------------------------------
    # 自动生成 config.json（供 setup.py 调用）
    # ----------------------------------------------------
    @staticmethod
    def auto_generate(instance_dir, instance_name=None, mc_port=25565, panel_port=15000):
        """
        对外统一入口：
        - 自动生成 config.json
        - 自动创建 ConfigModel 实例
        """

        if instance_name is None:
            instance_name = os.path.basename(instance_dir)

        config_path = os.path.join(instance_dir, "config.json")

        cfg = ConfigModel(config_path)
        cfg.data = ConfigModel.generate_default(
            instance_name=instance_name,
            instance_dir=instance_dir,
            mc_port=mc_port,
            panel_port=panel_port,
        )

        # ⭐ 必须写入，否则 systemd 服务名会变成 Python 类名
        cfg.data["instance"]["name"] = instance_name

        cfg.save()
        return cfg
