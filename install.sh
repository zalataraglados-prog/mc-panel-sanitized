#!/usr/bin/env bash
set -e

echo "======================================"
echo "  Minecraft 多实例部署器 - 一键安装"
echo "======================================"

# ─────────────────────────────
# 必须 root
# ─────────────────────────────
if [ "$EUID" -ne 0 ]; then
    echo "[ERROR] 请使用 root 运行： sudo bash install.sh"
    exit 1
fi

# ─────────────────────────────
# 基础工具
# ─────────────────────────────
if ! command -v git &> /dev/null; then
    echo "[INFO] 正在安装 git..."
    apt update
    apt install -y git
fi

if ! command -v python3 &> /dev/null; then
    echo "[INFO] 正在安装 Python3..."
    apt install -y python3 python3-pip
fi

# Docker 只检测，不强装（避免污染系统）

if ! command -v docker &> /dev/null; then
    echo "[WARN] 未检测到 Docker，请确保已手动安装并配置完成"
fi

INSTALL_DIR="/opt/mc-panel-sanitized"

# ─────────────────────────────
# 克隆 / 更新仓库（demo1）
# ─────────────────────────────
if [ ! -d "$INSTALL_DIR" ]; then
    echo "[INFO] 正在克隆仓库（demo1 分支）..."
    git clone -b demo1 --single-branch \
        https://github.com/zalataraglados-prog/mc-panel-sanitized.git \
        "$INSTALL_DIR"
else
    echo "[INFO] 仓库已存在，正在更新（demo1 分支）..."
    cd "$INSTALL_DIR"
    git fetch
    git checkout demo1
    git pull
fi

# ─────────────────────────────
# Python 依赖（最小）
# ─────────────────────────────
cd "$INSTALL_DIR"

if [ -f "requirements.txt" ]; then
    echo "[INFO] 安装 Python 依赖..."
    pip3 install -r requirements.txt
fi

# ─────────────────────────────
# 完成提示
# ─────────────────────────────
echo ""
echo "======================================"
echo "  ✅ 安装完成"
echo "======================================"
echo ""
echo "下一步："
echo "  1) 进入部署器目录："
echo "     cd $INSTALL_DIR"
echo ""
echo "  2) 查看部署计划："
echo "     python3 deploy/cli.py plan"
echo ""
echo "  3) 执行部署："
echo "     python3 deploy/cli.py apply"
echo ""
echo "======================================"