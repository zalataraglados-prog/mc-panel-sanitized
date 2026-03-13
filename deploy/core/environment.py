import os
import shutil
from deploy.utils.logger import log_info, log_error, log_warn


class EnvironmentChecker:

    # ------------------------------------------
    # 基础检查
    # ------------------------------------------
    def is_installed(self, cmd):
        """检查命令是否可执行（是否安装）"""
        return shutil.which(cmd) is not None

    # ------------------------------------------
    # Docker 检查与安装
    # ------------------------------------------
    def check_docker(self):
        return self.is_installed("docker")

    def install_docker(self):
        log_info("正在自动安装 Docker（来自官方脚本 get.docker.com）...")
        result = os.system("curl -fsSL https://get.docker.com | sh")

        if result != 0:
            log_error("Docker 安装失败，请检查网络或手动安装。")
            raise RuntimeError("Docker 安装失败")

        log_info("Docker 安装完成！")

    def start_docker(self):
        log_info("启动 Docker 服务...")
        os.system("systemctl enable docker")
        os.system("systemctl start docker")

    # ------------------------------------------
    # Compose 检查与安装
    # ------------------------------------------
    def check_compose(self):
        """检查 docker compose（新版本）"""
        return os.system("docker compose version > /dev/null 2>&1") == 0

    def install_compose_fallback(self):
        log_warn("未检测到 docker compose，使用 pip 安装旧版 docker-compose（fallback）...")
        os.system("pip3 install docker-compose > /dev/null 2>&1")

        if not self.is_installed("docker-compose"):
            log_error("docker-compose 安装失败，请检查 Python 或 pip 配置")
            raise RuntimeError("docker-compose 安装失败")

        log_info("docker-compose 已安装（fallback 版本）")

    # ------------------------------------------
    # 完整环境检查
    # ------------------------------------------
    def ensure_all(self):
        log_info("开始检查运行环境...")

        # --- Docker ---
        if not self.check_docker():
            log_warn("未检测到 Docker，将自动安装。")
            self.install_docker()
        else:
            log_info("Docker 已安装。")

        # --- Docker 服务 ---
        self.start_docker()

        # --- Compose ---
        if self.check_compose():
            log_info("docker compose 已安装。")
        else:
            log_warn("未检测到 docker compose，将自动安装。")
            self.install_compose_fallback()

        log_info("环境检查完成！Docker 与 Compose 已就绪。")
