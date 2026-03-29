import os
from deploy.utils.logger import log_info, log_error


class Composer:
    """
    docker-compose.yml 生成器

    根据 config.json 生成实例独立的 compose 文件。
    """

    def __init__(self, cfg, instance_dir: str, web_panel_path: str):
        self.cfg = cfg
        self.dir = instance_dir
        self.panel_path = web_panel_path

    # ----------------------------------------------------------------------
    # 辅助生成函数
    # ----------------------------------------------------------------------

    def _generate_env_block(self, env_dict: dict) -> str:
        """把 dict 转换成 YAML 的 environment: 块"""
        if not env_dict:
            return ""

        lines = []
        for key, val in env_dict.items():
            lines.append(f"      - {key}=\"{val}\"")
        return "\n".join(lines)

    def _generate_volumes_block(self, volumes_dict: dict) -> str:
        """把 dict 转换成 YAML 的 volumes: 块"""
        if not volumes_dict:
            return ""

        lines = []
        for key, val in volumes_dict.items():
            # 映射路径类似 "./data:/data"
            lines.append(f"      - {val}")
        return "\n".join(lines)

    # ----------------------------------------------------------------------
    # 主生成函数
    # ----------------------------------------------------------------------

    def generate(self):
        """生成 docker-compose.yml 文件"""

        log_info("正在生成 docker-compose.yml ...")

        docker = self.cfg.data["docker"]
        minecraft = self.cfg.data["minecraft"]
        network = self.cfg.data["network"]
        security = self.cfg.data.get("security", {})
        paths = self.cfg.data["paths"]

        rcon_bind = str(network.get("rcon_bind", "127.0.0.1") or "").strip()
        rcon_public = bool(security.get("rcon_public", False))
        if rcon_public or rcon_bind in ("", "0.0.0.0", "*"):
            rcon_mapping = f'{network["rcon_port"]}:25575'
        else:
            rcon_mapping = f'{rcon_bind}:{network["rcon_port"]}:25575'
        rcon_password = str(security.get("rcon_password", "") or "").strip()
        if rcon_password:
            os.environ.setdefault("MC_PANEL_RCON_PASSWORD", rcon_password)

        env_extra = self._generate_env_block(docker.get("extra_env", {}))
        vol_extra = self._generate_volumes_block(docker.get("volumes", {}))

        compose_content = f"""version: '3'

services:

  minecraft:
    image: {docker["image"]}:{docker["tag"]}
    container_name: {self.cfg.instance_name}-minecraft
    restart: {docker["restart_policy"]}
    ports:
      - "{network["mc_port"]}:25565"
      - "{rcon_mapping}"
    environment:
      - EULA=TRUE
      - VERSION={minecraft["version"]}
      - MEMORY={minecraft["jvm"]["memory"]}
      - ENABLE_RCON=TRUE
      - RCON_PASSWORD=${{MC_PANEL_RCON_PASSWORD}}
      - RCON_PORT={network["rcon_port"]}
 {env_extra}
    volumes:
{vol_extra}
    networks:
      - default

networks:
  default:
    driver: bridge
"""

        compose_path = os.path.join(self.dir, "docker-compose.yml")

        with open(compose_path, "w") as f:
            f.write(compose_content)

        log_info(f"docker-compose.yml 已生成：{compose_path}")
