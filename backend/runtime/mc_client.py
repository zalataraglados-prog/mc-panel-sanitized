from typing import Dict


class MCClient:
    def __init__(self, instance_dir: str):
        self.instance_dir = instance_dir

    def status(self) -> Dict[str, bool]:
        return {"running": True}
