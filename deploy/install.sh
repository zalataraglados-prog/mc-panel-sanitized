#!/bin/bash

set -e

echo "======================================"
echo "  Minecraft 多实例部署器 - 一键安装"
echo "======================================"

# 必须 root
if [ "$EUID" -ne 0 ]; then
    echo "请使用 root 运行： sudo bash install.sh"
    exit 1
fi

# 安装 git
if ! command -v git &> /dev/null; then
    echo "[INFO] 正在安装 git..."
    apt update && apt install -y git
fi

# 仓库将被放置的位置
INSTALL_DIR="/opt/mc-panel-sanitized"

# 当前 install.sh 所在目录（deploy）
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)

# 仓库根目录应是 SCRIPT_DIR 的上一层
REPO_DIR=$(dirname "$SCRIPT_DIR")

# 如果 /opt/mc-panel-sanitized 不存在 → clone
if [ ! -d "$INSTALL_DIR" ]; then
    echo "[INFO] 正在克隆仓库..."
    git clone https://github.com/zalataraglados-prog/mc-panel-sanitized.git "$INSTALL_DIR"
else
    echo "[INFO] 仓库已存在，正在更新..."
    cd "$INSTALL_DIR"
    git pull
fi

# 确保 python3 存在
if ! command -v python3 &> /dev/null; then
    echo "[INFO] 正在安装 Python3..."
    apt install -y python3 python3-pip
fi

# 切换到部署器所在目录（deploy）
cd "$INSTALL_DIR/deploy"

echo "[INFO] 开始执行部署器..."
python3 setup.py

echo ""
echo "======================================"
echo "     🚀 部署完成！实例已启动！"
echo "======================================"
