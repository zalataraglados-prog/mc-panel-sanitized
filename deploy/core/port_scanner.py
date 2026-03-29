import socket
from deploy.utils.logger import log_info, log_warn, log_error

class PortScanner:
    """
    端口扫描器：
    - 检查端口是否被占用
    - 自动从指定起点查找可用端口
    """

    @staticmethod
    def is_free(port, host="0.0.0.0"):
        """
        检查端口是否可用：
        - 尝试绑定 TCP
        - 成功 = 可用
        - 失败 = 正在占用
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind((host, port))
            s.close()
            return True
        except OSError:
            return False

    @staticmethod
    def find_free(start_port=25565, max_tries=200, host="0.0.0.0"):
        """
        从 start_port 开始向上寻找可用端口
        默认检查 200 个，够你疯狂部署 200 条实例不撞车。
        """

        port = start_port

        for _ in range(max_tries):
            if PortScanner.is_free(port, host):
                log_info(f"找到可用端口：{port}")
                return port
            port += 1

        # 超过检查次数仍找不到，说明服务器端口区间爆炸
        log_error(f"无法找到可用端口（从 {start_port} 开始检查了 {max_tries} 个）")
        raise RuntimeError("端口不足，无法自动分配。")
