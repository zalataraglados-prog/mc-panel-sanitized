import os
from utils.logger import log_info, log_error


class Deployer:
    """
    部署执行层：
    - systemd daemon-reload
    - systemctl enable
    - systemctl start
    - 输出结果
    """

    def __init__(self, instance_name: str, instance_dir: str):
        self.name = instance_name
        self.dir = instance_dir
        self.service = f"mc-{instance_name}.service"

    # --------------------------------------------------------------
    # 辅助执行函数
    # --------------------------------------------------------------

    def _run(self, cmd: str) -> int:
        """安全执行命令并返回退出码"""
        log_info(f"执行命令：{cmd}")
        return os.system(cmd)

    # --------------------------------------------------------------
    # 主执行逻辑
    # --------------------------------------------------------------

    def run(self):
        log_info("开始部署实例...")

        # 1. systemd 重载
        if self._run("systemctl daemon-reload") != 0:
            log_error("systemd 重载失败")
            raise RuntimeError("systemctl daemon-reload 失败")

        # 2. 启用服务
        if self._run(f"systemctl enable {self.service}") != 0:
            log_error("systemctl enable 失败")
            raise RuntimeError("systemctl enable 失败")

        # 3. 启动服务
        if self._run(f"systemctl start {self.service}") != 0:
            log_error("systemctl start 失败")
            raise RuntimeError("systemctl start 失败")

        # 4. 检查服务状态
        log_info("正在检查服务状态...")
        status_code = os.system(f"systemctl is-active --quiet {self.service}")

        if status_code == 0:
            log_info("实例启动成功！")
        else:
            log_error("实例启动失败，请查看 systemctl status 或 logs。")
            raise RuntimeError("实例启动失败")

        # 5. 输出最终信息
        log_info("部署流程已完成。")
        log_info(f"systemd 服务：{self.service}")
        log_info(f"实例目录：{self.dir}")