import os
from utils.logger import log_info, log_error
from utils.file_helper import FileHelper


class ComposeGenerator:
    """
    使用模板 docker-compose.yml.tpl 生成实例的 compose 文件
    """

    def __init__(self, cfg, instance_dir: str, web_panel_path: str, templates_dir="templates"):
        self.cfg = cfg
        self.instance_dir = instance_dir
        self.panel_path = web_panel_path
        self.templates_dir = templates_dir

    def _template_path(self):
        """返回 compose 模板路径"""
        return os.path.join(self.templates_dir, "docker-compose.yml.tpl")

    def generate(self):
        """从模板渲染 docker-compose.yml"""

        log_info("正在使用模板生成 docker-compose.yml ...")

        tpl_path = self._template_path()

        if not os.path.exists(tpl_path):
            log_error(f"模板文件不存在：{tpl_path}")
            raise FileNotFoundError("docker-compose.yml.tpl 不存在")

        template = FileHelper.load_file(tpl_path)

        data = self.cfg.data

        # 构建渲染变量
        vars = {
            "INSTANCE_NAME": data["instance"]["name"],
            "DOCKER_IMAGE": data["docker"]["image"],
            "DOCKER_TAG": data["docker"]["tag"],
            "RESTART_POLICY": data["docker"]["restart_policy"],

            "MC_PORT": data["network"]["mc_port"],
            "RCON_PORT": data["network"]["rcon_port"],
            "PANEL_PORT": data["network"]["panel_port"],

            "MC_VERSION": data["minecraft"]["version"],
            "MC_MEMORY": data["minecraft"]["jvm"]["memory"],

            "PANEL_BUILD_PATH": self.panel_path
        }

        # extra_env → ENV_BLOCK（模板要求换行格式）
        env_block = ""
        for k, v in data["docker"]["extra_env"].items():
            env_block += f"      - {k}=\"{v}\"\n"
        vars["ENV_BLOCK"] = env_block.rstrip()

        # volumes → VOLUME_BLOCK
        vol_block = ""
        for _, mapping in data["docker"]["volumes"].items():
            vol_block += f"      - {mapping}\n"
        vars["VOLUME_BLOCK"] = vol_block.rstrip()

        # 渲染
        output = FileHelper.render_template(template, vars)

        # 写入文件
        dest = os.path.join(self.instance_dir, "docker-compose.yml")
        FileHelper.write_file(dest, output)

        log_info(f"docker-compose.yml 已生成：{dest}")