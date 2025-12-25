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

echo ""
IMPORT_STRING=$(read_tty "Paste claims string (or press Enter to continue): ")
if [ -n "$IMPORT_STRING" ]; then
  echo ""
  echo "[INFO] Running plan from imported claims..."
  python3 -m deploy.cli plan \
    --import-string "$IMPORT_STRING"

  echo ""
  echo "可复用配置串："
  echo "$IMPORT_STRING"
  echo ""
  echo "[INFO] Review complete. Deployment is not executed in Phase 10."
  exit 0
fi

cd "$INSTALL_DIR"

echo ""
VERSION=$(read_tty "请输入 Minecraft 版本（如 1.21.4）：")
if [ -z "$VERSION" ]; then
  VERSION="1.21.4"
fi

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

echo ""
echo "Select server stack:"
echo "1) vanilla"
echo "2) paper (recommended)"
echo "3) fabric"
echo "4) forge"
echo "5) neoforge"
STACK_CHOICE=$(read_tty "Enter [1-5]: " )

case "$STACK_CHOICE" in
  1) STACK_TYPE="vanilla" ;;
  3) STACK_TYPE="fabric" ;;
  4) STACK_TYPE="forge" ;;
  5) STACK_TYPE="neoforge" ;;
  *) STACK_TYPE="paper" ;;
esac

echo ""
echo "Select Java runtime:"
echo "1) auto (based on Minecraft version)"
echo "2) 8"
echo "3) 11"
echo "4) 16"
echo "5) 17"
RUNTIME_CHOICE=$(read_tty "Enter [1-5]: " )

case "$RUNTIME_CHOICE" in
  2) RUNTIME_JAVA="8" ;;
  3) RUNTIME_JAVA="11" ;;
  4) RUNTIME_JAVA="16" ;;
  5) RUNTIME_JAVA="17" ;;
  *) RUNTIME_JAVA="auto" ;;
esac

MEMORY=$(read_tty "请输入分配内存（如 2G / 4G）：")
VIEW_DISTANCE=$(read_tty "请输入 view-distance（推荐 6~10）：")

PLAN_OUTPUT=$(python3 -m deploy.cli plan \
  --version "$VERSION" \
  --profile "$PROFILE" \
  --set edition="$EDITION" \
  --set stack.type="$STACK_TYPE" \
  --set runtime.java="$RUNTIME_JAVA" \
  --set docker.env.MEMORY="$MEMORY" \
  --set minecraft.view_distance="$VIEW_DISTANCE")
echo "$PLAN_OUTPUT"
LEVEL=$(echo "$PLAN_OUTPUT" | sed -n 's/^Level:[[:space:]]*//p' | head -n 1)

case "$LEVEL" in
  block)
    echo "[INFO] Review blocked. Deployment stopped."
    exit 1
    ;;
  warn)
    CONFIRM=$(read_tty "Review contains warnings. Continue? [y/N] ")
    case "$CONFIRM" in
      y|Y) echo "[INFO] Review accepted. Deployment remains disabled in Phase 10." ;;
      *) echo "[INFO] Deployment canceled."; exit 0 ;;
    esac
    ;;
  *)
    echo "[INFO] Review passed. Deployment remains disabled in Phase 10."
    ;;
esac

echo ""
echo "======================================"
echo "  部署流程已完成"
echo "======================================"
