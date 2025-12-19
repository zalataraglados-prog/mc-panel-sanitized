from deploy.core.composer import Composer
from deploy.core.systemd_gen import SystemdGenerator
from deploy.core.deployer import Deployer
from deploy.core.config_model import ConfigModel
from deploy.context import InstanceContext


def apply_legacy_config(*, cfg: ConfigModel, ctx: InstanceContext):
    """
    Apply legacy config using existing core modules.
    """

    # 1. 生成 docker-compose / 配置文件
    composer = Composer(
        cfg=cfg,
        instance_dir=ctx.instance_dir,
        web_panel_path=None,  # demo1 不构建 panel
    )
    composer.generate()

    # 2. systemd
    systemd = SystemdGenerator(
        ctx.instance_name,
        ctx.instance_dir,
    )
    systemd.generate()

    # 3. 启动
    deployer = Deployer(
        ctx.instance_name,
        ctx.instance_dir,
    )
    deployer.run()
