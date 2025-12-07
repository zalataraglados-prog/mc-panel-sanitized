import os

from core.environment import EnvironmentChecker
from core.instance_namer import InstanceNamer
from core.config_model import ConfigModel
from core.composer import Composer
from core.systemd_gen import SystemdGenerator
from core.deployer import Deployer


BASE_INST_DIR = "/opt/mc-instances"
PANEL_SRC_DIR = "/opt/mc-panel-sanitized/web-panel"


def main():
    print("[INFO] Minecraft 自动部署器启动")

    # 1. 环境检查：Docker + Compose
    env = EnvironmentChecker()
    print("[INFO] 开始检查运行环境...")
    env.ensure_all()
    print("[INFO] 环境检查完成！Docker 与 Compose 已就绪。\n")

    # 2. 创建实例根目录
    os.makedirs(BASE_INST_DIR, exist_ok=True)

    # 3. 获取实例名（正确入口）
    instance_name = InstanceNamer.ask_name(BASE_INST_DIR)

    # 4. 创建实例目录
    inst_dir = os.path.join(BASE_INST_DIR, instance_name)
    os.makedirs(inst_dir, exist_ok=True)
    print(f"[INFO] 实例目录已创建：{inst_dir}")

    # 5. 自动生成配置文件
    cfg_obj = ConfigModel.auto_generate(inst_dir, instance_name)

    # 设置 web-panel 构建路径
    cfg_obj.data.setdefault("panel", {})
    cfg_obj.data["panel"]["build_path"] = PANEL_SRC_DIR
    cfg_obj.save()
    print(f"[INFO] Config 已保存：{cfg_obj.path}")

    # 6. 生成 docker-compose.yml
    composer = Composer(
        cfg=cfg_obj,
        instance_dir=inst_dir,
        web_panel_path=PANEL_SRC_DIR,
    )
    composer.generate()

    # 7. 生成 systemd 服务（签名：instance_name, instance_dir）
    systemd = SystemdGenerator(cfg_obj.instance_name, inst_dir)
    systemd.generate()

    # 8. 部署（签名：cfg, instance_dir）
    dp = Deployer(cfg_obj, inst_dir)
    print("[INFO] 开始部署实例...")
    dp.run()


if __name__ == "__main__":
    main()
