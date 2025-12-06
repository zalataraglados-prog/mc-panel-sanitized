#!/usr/bin/env python3
import os
import sys
from utils.logger import log_info, log_error
from core.environment import EnvironmentChecker
from core.instance_namer import InstanceNamer
from core.instance_creator import InstanceCreator
from core.config_model import ConfigModel
from core.composer import ComposeGenerator
from core.systemd_gen import SystemdGenerator
from core.deployer import Deployer

# 实例根路径
BASE_PATH = "/opt/mc-instances"
WEB_PANEL_PATH = "../web-panel"  # 固定路径

def ensure_root():
    if os.geteuid() != 0:
        log_error("请使用 root 用户运行部署器。")
        sys.exit(1)

def main():
    log_info("Minecraft 自动部署器启动")

    # 1. 检查 root 权限
    ensure_root()

    # 2. 环境检查（Docker + Compose）
    env = EnvironmentChecker()
    env.ensure_all()

    # 3. 询问实例名
    name = InstanceNamer.ask_name(BASE_PATH)

    # 4. 创建实例目录
    inst_dir = InstanceCreator.create_structure(BASE_PATH, name)

    # 5. 创建 config.json
    cfg_obj = ConfigModel.auto_generate(inst_dir)
    cfg_obj.save()

    # 6. 生成 docker-compose.yml
    cg = ComposeGenerator(cfg_obj, inst_dir, WEB_PANEL_PATH)
    cg.generate()

    # 7. 生成 systemd
    sg = SystemdGenerator(name, inst_dir)
    sg.generate()

    # 8. 部署（compose up + systemd enable/start）
    dp = Deployer(name, inst_dir)
    dp.run()

    log_info("部署完成！服务器已启动。")
    print()
    print("========== 实例信息 ==========")
    print(f"实例名称：{name}")
    print(f"实例路径：{inst_dir}")
    print(f"MC 端口：{cfg_obj.mc_port}")
    print(f"Web 面板端口：{cfg_obj.panel_port}")
    print(f"systemd 服务名：mc-{name}.service")
    print("============================")

if __name__ == "__main__":
    main()
