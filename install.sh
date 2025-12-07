#!/bin/bash

set -e

echo "======================================"
echo "     Minecraft 多实例部署器 - 一键安装"
echo "======================================"

# 1. 必须 root
if [ "$EUID" -ne 0 ]; then
    echo "请使用： sudo bash install.sh"
    exit 1
fi

# 2. 安装必要软件
if ! command -v git &> /dev/null; then
    echo "[INFO] 安装 git..."
    apt update && apt install -y git
fi

if ! command -v python3 &> /dev/null; then
    echo "[INFO] 安装 Python3..."
    apt install -y python3 python3-pip
fi

# 3. 安装 Docker（如缺）
if ! command -v docker &> /dev/null; then
    echo "[INFO] 安装 Docker..."
    apt install -y docker.io
    systemctl enable docker
    systemctl start docker
fi

# 4. 克隆或更新仓库
INSTALL_DIR="/opt/mc-panel-sanitized"

if [ ! -d "$INSTALL_DIR" ]; then
    echo "[INFO] 克隆仓库中..."
    git clone https://github.com/zalataraglados-prog/mc-panel-sanitized.git "$INSTALL_DIR"
else
    echo "[INFO] 仓库已存在，正在更新..."
    cd "$INSTALL_DIR"
    git pull
fi

# 5. 进入部署器目录
cd "$INSTALL_DIR/deploy"

echo "[INFO] 执行部署器..."
python3 setup.py

echo ""
echo "======================================"
echo "  🚀 部署完成！Minecraft 实例已启动！"
echo "======================================"
