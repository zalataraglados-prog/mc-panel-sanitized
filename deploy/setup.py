import os
import subprocess
from core.environment import EnvironmentChecker
from core.instance_namer import InstanceNamer
from core.config_model import ConfigModel
from core.composer import Composer
from core.systemd_gen import SystemdGenerator
from core.deployer import Deployer


def main():
    print("[INFO] Minecraft 自动部署器启动")

    # 环境检查：Docker + Compose
    env = EnvironmentChecker()
    print("[INFO] 开始检查运行环境...")
    env.ensure_all()
    print("[INFO] 环境检查完成！Docker 与 Compose 已就绪。\n")

    # 用户输入实例名称
    instance_name = input("请输入实例名称（留空自动生成）： ").strip()
    if not instance_name:
        instance_name = InstanceNamer.generate()
        print(f"[INFO] 已自动生成实例名：{instance_name}")

    # 实例目录
    inst_dir = f"/opt/mc-instances/{instance_name}"
    os.makedirs(inst_dir, exist_ok=True)
    print(f"[INFO] 实例目录已创建：{inst_dir}")

    # 生成配置文件
    cfg_obj = ConfigModel.auto_generate(inst_dir, instance_name)

    # ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
    # 设置 Web Panel 的构建目录（关键！）
    cfg_obj.data["panel"]["build_path"] = "/opt/mc-panel-sanitized/web-panel"
    cfg_obj.save()
    print(f"[INFO] Config 已保存：{cfg_obj.path}")
    # ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑

    # 生成 docker-compose.yml
    composer = Composer(cfg_obj)
    composer.render()
    print(f"[INFO] docker-compose.yml 已生成：{composer.output_path}")

    # 写入 systemd 服务
    systemd = SystemdGenerator(cfg_obj)
    systemd.write()
    print(f"[INFO] systemd 服务已写入：{systemd.output_path}")

    # 使用 systemd 部署（或失败 fallback）
    dp = Deployer(cfg_obj)
    print("[INFO] 开始部署实例...")
    dp.run()


if __name__ == "__main__":
    main()
