from dataclasses import dataclass


@dataclass
class InstanceContext:
    instance_name: str
    instance_dir: str
    mc_port: int
    panel_port: int
