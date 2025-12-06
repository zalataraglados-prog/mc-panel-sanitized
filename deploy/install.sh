#!/bin/bash

set -e

echo "======================================"
echo "  Minecraft 多实例部署器 - 一键安装"
echo "======================================"

# 1. 必须 root
if [ "$EUID" -ne 0 ]; then
    echo "请使用 root 运行： sudo bash install.sh"
    exit 1
fi

# 2. 安装 git（如果没有）
if ! command -v git &> /dev/null; then
    echo "[INFO] 正在安装 git..."
    apt update && apt install -y git
fi

# 3. 克隆仓库或更新
INSTALL_DIR="/opt/minecraft-deployer"

if [ ! -d "$INSTALL_DIR" ]; then
    echo "[INFO] 正在克隆仓库..."
    git clone https://github.com/<你的用户名>/<你的仓库>.git "$INSTALL_DIR"
else
    echo "[INFO] 仓库已存在，正在更新..."
    cd "$INSTALL_DIR"
    git pull
fi

# 4. 检查 python3
if ! command -v python3 &> /dev/null; then
    echo "[INFO] 正在安装 Python3..."
    apt install -y python3 python3-pip
fi

# 5. 执行部署器
cd "$INSTALL_DIR/deploy"

echo "[INFO] 开始执行部署器..."
python3 setup.py

echo ""
echo "======================================"
echo "     🚀 部署完成！实例已启动！"
echo "======================================"