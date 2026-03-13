import sys

# ANSI 颜色代码
COLOR_RESET = "\033[0m"
COLOR_INFO = "\033[94m"    # 蓝色
COLOR_WARN = "\033[93m"    # 黄色
COLOR_ERROR = "\033[91m"   # 红色
COLOR_OK = "\033[92m"      # 绿色


def _print(prefix: str, msg: str, color: str):
    """统一打印格式"""
    sys.stdout.write(f"{color}{prefix}{COLOR_RESET} {msg}\n")
    sys.stdout.flush()


def log_info(msg: str):
    _print("[INFO]", msg, COLOR_INFO)


def log_warn(msg: str):
    _print("[WARN]", msg, COLOR_WARN)


def log_error(msg: str):
    _print("[ERROR]", msg, COLOR_ERROR)


def log_ok(msg: str):
    _print("[OK]", msg, COLOR_OK)
