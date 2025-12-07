import os
from utils.logger import log_info, log_error


class SystemdGenerator:
    """
    为实例生成 systemd 服务文件：
    控制 docker compose up / down
    """

    def __init__(self, instance_name: str, instance_dir: str):
        self.name = instance_name
        self.dir = instance_dir

    def generate(self):
        """生成 systemd 服务文件"""

        log_info("正在生成 systemd 服务...")

        service_name = f"mc-{self.name}.service"
        service_path = f"/etc/systemd/system/{service_name}"

        # WSL / Linux 通用的 docker compose 绝对路径
        compose_exec = "/usr/local/lib/docker/cli-plugins/docker-compose"

        content = f"""
[Unit]
Description=Minecraft Instance {self.name}
After=network.target docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=true
WorkingDirectory={self.dir}
ExecStart={compose_exec} -p {self.name} up -d
ExecStop={compose_exec} -p {self.name} down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
"""

        try:
            with open(service_path, "w") as f:
                f.write(content)
        except Exception as e:
            log_error(f"写入 systemd 服务失败：{e}")
            raise

        log_info(f"systemd 服务已写入：{service_path}")
        return service_path
