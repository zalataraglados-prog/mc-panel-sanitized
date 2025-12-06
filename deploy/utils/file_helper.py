import os
from utils.logger import log_info, log_warn, log_error


class FileHelper:
    """
    文件写入工具：
    - 标准化写文件流程
    - 自动创建目录
    - 安全覆盖写入
    - 未来可扩展模板渲染逻辑
    """

    @staticmethod
    def ensure_dir(path: str):
        """确保目录存在，不存在则创建"""
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            log_info(f"已创建目录：{path}")

    @staticmethod
    def write_file(path: str, content: str, backup=False):
        """
        写入文件（安全写入）
        - 自动创建上级目录
        - 可选备份旧文件
        """

        dir_path = os.path.dirname(path)
        FileHelper.ensure_dir(dir_path)

        # 备份旧文件
        if backup and os.path.exists(path):
            backup_path = path + ".bak"
            os.rename(path, backup_path)
            log_warn(f"已有文件备份为：{backup_path}")

        # 写入临时文件，确保写入完整性
        tmp_path = path + ".tmp"
        try:
            with open(tmp_path, "w") as f:
                f.write(content)
        except Exception as e:
            log_error(f"写入临时文件失败：{tmp_path}")
            raise

        # 覆盖移动到真正文件（原子操作）
        os.replace(tmp_path, path)

        log_info(f"文件已写入：{path}")

    @staticmethod
    def load_file(path: str) -> str:
        """读取文本文件"""
        if not os.path.exists(path):
            log_error(f"文件不存在：{path}")
            return ""

        with open(path, "r") as f:
            return f.read()

    @staticmethod
    def render_template(template: str, variables: dict) -> str:
        """
        模板渲染（简单占位符替换）
        支持 {{PLACEHOLDER}} 格式
        """

        content = template

        for key, value in variables.items():
            placeholder = "{{" + key + "}}"
            content = content.replace(placeholder, str(value))

        return content