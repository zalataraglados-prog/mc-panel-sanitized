#!/bin/bash
set -e

echo "======================================"
echo "  Minecraft 多实例部署器 - 一键安装"
echo "======================================"

# ------------------------------
# 必须使用 root
# ------------------------------
if [ "$EUID" -ne 0 ]; then
    echo "请使用 root 运行：sudo bash install.sh"
    exit 1
fi

# ------------------------------
# 检查 git 是否存在
# ------------------------------
if ! command -v git &> /dev/null; then
    echo "[INFO] 正在安装 git..."
    apt update && apt install -y git
fi

INSTALL_DIR="/opt/mc-panel-sanitized"
BRANCH="demon1.1"

# ------------------------------
# 克隆 / 更新 demon1.1 分支
# ------------------------------
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

# ------------------------------
# 交互式 Claims 构建
# ------------------------------
read_tty() {
  local prompt="$1"
  local var
  if [ -t 0 ]; then
    read -r -p "$prompt" var
  else
    read -r -p "$prompt" var < /dev/tty
  fi
  echo "$var"
}

cd "$INSTALL_DIR"

echo ""
echo "请选择 Minecraft 版本："
echo "1) Java Edition（插件 / 大型服务器）"
echo "2) Bedrock Edition（手机 / 主机 / Win10）"
EDITION_CHOICE=$(read_tty "请输入 [1-2]：")

case "$EDITION_CHOICE" in
  2) EDITION="bedrock" ;;
  *) EDITION="java" ;;
esac

if [ "$EDITION" = "bedrock" ]; then
  echo "[INFO] 当前选择：Bedrock Edition"
  echo ""
  echo "很抱歉，当前版本的部署器仅支持 Minecraft Java Edition。"
  echo "Bedrock Edition 的执行层尚未实现（Phase 6.2 以后）。"
  echo ""
  echo "你可以："
  echo "- 使用 Java Edition 重新部署"
  echo "- 或等待后续版本更新"
  exit 0
fi

echo ""
echo "请选择配置档位："
echo "1) beginner"
echo "2) normal（默认）"
echo "3) advanced"
PROFILE_CHOICE=$(read_tty "请输入 [1-3]：")

case "$PROFILE_CHOICE" in
  1) PROFILE="beginner" ;;
  3) PROFILE="advanced" ;;
  *) PROFILE="normal" ;;
esac

MEMORY=$(read_tty "请输入分配内存（如 2G / 4G）：")
VIEW_DISTANCE=$(read_tty "请输入 view-distance（推荐 6~10）：")

echo ""
echo "[INFO] 执行 plan（仅展示 Review）..."
python3 -m deploy.cli plan \
  --profile "$PROFILE" \
  --set edition="$EDITION" \
  --set docker.env.MEMORY="$MEMORY" \
  --set minecraft.view_distance="$VIEW_DISTANCE"

echo ""
CONFIRM=$(read_tty "是否确认使用以上配置部署？[y/N] ")

case "$CONFIRM" in
  y|Y)
    echo "[INFO] 执行 apply..."
    python3 -m deploy.cli apply \
      --profile "$PROFILE" \
      --set edition="$EDITION" \
      --set docker.env.MEMORY="$MEMORY" \
      --set minecraft.view_distance="$VIEW_DISTANCE"
    ;;
  *)
    echo "[INFO] 已取消部署。"
    exit 0
    ;;
esac

echo ""
echo "======================================"
echo "  部署流程已完成"
echo "======================================"
