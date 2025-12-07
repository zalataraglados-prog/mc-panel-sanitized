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

INSTALL_DIR="/opt/mc-panel-sanitized"

# 克隆 demo1 分支（关键修复）
if [ ! -d "$INSTALL_DIR" ]; then
    echo "[INFO] 正在克隆仓库（demo1 分支）..."
    git clone -b demo1 --single-branch https://github.com/zalataraglados-prog/mc-panel-sanitized.git "$INSTALL_DIR"
else
    echo "[INFO] 仓库已存在，正在更新（demo1 分支）..."
    cd "$INSTALL_DIR"
    git fetch
    git checkout demo1
    git pull
fi

# Python3
if ! command -v python3 &> /dev/null; then
    echo "[INFO] 正在安装 Python3..."
    apt install -y python3 python3-pip
fi

# 进入 deploy 目录执行部署器
cd "$INSTALL_DIR/deploy"
echo "[INFO] 执行部署器..."
python3 setup.py

echo ""
echo "======================================"
echo "  🚀 部署完成！Minecraft 实例已启动！"
echo "======================================"
