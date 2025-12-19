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
# 交互式 Claims 构建与确认
# ─────────────────────────────

cd /opt/mc-panel-sanitized

echo ""
echo "请选择配置档位："
echo "1) beginner"
echo "2) normal（默认）"
echo "3) advanced"
read -r -p "请输入 [1-3]：" PROFILE_CHOICE

case "$PROFILE_CHOICE" in
    1) PROFILE="beginner" ;;
    3) PROFILE="advanced" ;;
    *) PROFILE="normal" ;;
esac

read -r -p "请输入分配内存（如 2G / 4G）：" MEMORY
read -r -p "请输入 view-distance（推荐 6~10）：" VIEW_DISTANCE

echo ""
echo "[INFO] 执行 plan（仅展示 Review）..."
python3 -m deploy.cli plan \
  --profile "$PROFILE" \
  --set docker.env.MEMORY="$MEMORY" \
  --set minecraft.view_distance="$VIEW_DISTANCE"

echo ""
read -r -p "是否确认使用以上配置部署？[y/N] " CONFIRM
case "$CONFIRM" in
    y|Y)
        echo "[INFO] 执行 apply..."
        python3 -m deploy.cli apply \
          --profile "$PROFILE" \
          --set docker.env.MEMORY="$MEMORY" \
          --set minecraft.view_distance="$VIEW_DISTANCE"
        ;;
    *)
        echo "[INFO] 未确认，已退出。"
        exit 0
        ;;
esac

echo ""
echo "======================================"
echo "  部署流程已结束"
echo "======================================"
