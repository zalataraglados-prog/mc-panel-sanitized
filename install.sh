#!/bin/bash
set -e

echo "======================================"
echo "  Minecraft 多实例部署器 - 一键安装"
echo "======================================"

# ─────────────────────────────
# 必须 root
# ─────────────────────────────
if [ "$EUID" -ne 0 ]; then
    echo "请使用 root 运行： sudo bash install.sh"
    exit 1
fi

# ─────────────────────────────
# 安装 git（最小依赖）
# ─────────────────────────────
if ! command -v git &> /dev/null; then
    echo "[INFO] 正在安装 git..."
    apt update && apt install -y git
fi

INSTALL_DIR="/opt/mc-panel-sanitized"
BRANCH="demon1.1"

# ─────────────────────────────
# 克隆 / 更新仓库（demon1.1）
# ─────────────────────────────
if [ ! -d "$INSTALL_DIR" ]; then
    echo "[INFO] 正在克隆仓库（$BRANCH 分支）..."
    git clone -b "$BRANCH" --single-branch \
        https://github.com/zalataraglados-prog/mc-panel-sanitized.git \
        "$INSTALL_DIR"
else
    echo "[INFO] 仓库已存在，正在更新（$BRANCH 分支）..."
    cd "$INSTALL_DIR"
    git fetch
    git checkout "$BRANCH"
    git pull
fi

# ─────────────────────────────
# 进入部署器入口并立即执行
# ─────────────────────────────
cd "$INSTALL_DIR/deploy"

echo "[INFO] 执行部署器..."

python3 -m deploy.cli plan
python3 -m deploy.cli apply

echo ""
echo "======================================"
echo "  🚀 部署流程已结束"
echo "======================================"
