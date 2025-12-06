import os
from utils.logger import log_info, log_error
from utils.file_helper import FileHelper


class SystemdGenerator:
    """
    使用模板生成 systemd 服务文件：
    - minecraft.service
    - mc-panel.service
    """

    def __init__(self, instance_name: str, instance_dir: str, templates_dir="templates"):
        self.name = instance_name
        self.dir = instance_dir
        self.templates_dir = templates_dir

    # ----------------------------------------------------
    # 获取模板路径
    # ----------------------------------------------------
    def _tpl_mc(self):
        return os.path.join(self.templates_dir, "minecraft.service.tpl")

    def _tpl_panel(self):
        return os.path.join(self.templates_dir, "mc-panel.service.tpl")

    # ----------------------------------------------------
    # 渲染并写入 systemd 文件
    # ----------------------------------------------------
    def _render_and_write(self, tpl_path: str, dest_path: str, vars: dict):
        if not os.path.exists(tpl_path):
            log_error(f"模板文件不存在：{tpl_path}")
            raise FileNotFoundError(tpl_path)

        tpl = FileHelper.load_file(tpl_path)
        content = FileHelper.render_template(tpl, vars)

        FileHelper.write_file(dest_path, content)

        log_info(f"Systemd 服务已生成：{dest_path}")

    # ----------------------------------------------------
    # 主生成函数
    # ----------------------------------------------------
    def generate(self):
        log_info("正在生成 systemd 服务文件...")

        # systemd 要求绝对路径
        mc_service_path = f"/etc/systemd/system/mc-{self.name}.service"
        panel_service_path = f"/etc/systemd/system/mc-{self.name}-panel.service"

        # 模板变量
        vars = {
            "INSTANCE_NAME": self.name,
            "INSTANCE_DIR": self.dir
        }

        # Minecraft 服务
        self._render_and_write(self._tpl_mc(), mc_service_path, vars)

        # Panel 服务
        self._render_and_write(self._tpl_panel(), panel_service_path, vars)

        return mc_service_path, panel_service_path