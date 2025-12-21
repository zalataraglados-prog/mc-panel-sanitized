#!/bin/bash
set -e

echo "======================================"
echo "  Minecraft ?????? - ????"
echo "======================================"

# ------------------------------
# ?? root
# ------------------------------
if [ "$EUID" -ne 0 ]; then
    echo "??? root ??? sudo bash install.sh"
    exit 1
fi

# ------------------------------
# ?? git??????
# ------------------------------
if ! command -v git &> /dev/null; then
    echo "[INFO] ???? git..."
    apt update && apt install -y git
fi

INSTALL_DIR="/opt/mc-panel-sanitized"
BRANCH="demon1.1"

# ------------------------------
# ?? / ?????demon1.1?
# ------------------------------
if [ ! -d "$INSTALL_DIR" ]; then
    echo "[INFO] ???????$BRANCH ???..."
    git clone -b "$BRANCH" --single-branch         https://github.com/zalataraglados-prog/mc-panel-sanitized.git         "$INSTALL_DIR"
else
    echo "[INFO] ???????????$BRANCH ???..."
    cd "$INSTALL_DIR"
    git fetch
    git checkout "$BRANCH"
    git pull
fi

# ------------------------------
# ??? Claims ?????
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

cd /opt/mc-panel-sanitized

echo ""
echo "????????"
echo "1) beginner"
echo "2) normal????"
echo "3) advanced"
PROFILE_CHOICE=$(read_tty "??? [1-3]?")

case "$PROFILE_CHOICE" in
  1) PROFILE="beginner" ;;
  3) PROFILE="advanced" ;;
  *) PROFILE="normal" ;;
esac

MEMORY=$(read_tty "????????? 2G / 4G??")
VIEW_DISTANCE=$(read_tty "??? view-distance??? 6~10??")

echo ""
echo "[INFO] ?? plan???? Review?..."
python3 -m deploy.cli plan   --profile "$PROFILE"   --set docker.env.MEMORY="$MEMORY"   --set minecraft.view_distance="$VIEW_DISTANCE"

echo ""
CONFIRM=$(read_tty "?????????????[y/N] ")
case "$CONFIRM" in
  y|Y)
    echo "[INFO] ?? apply..."
    python3 -m deploy.cli apply       --profile "$PROFILE"       --set docker.env.MEMORY="$MEMORY"       --set minecraft.view_distance="$VIEW_DISTANCE"
    ;;
  *)
    echo "[INFO] ??????"
    exit 0
    ;;
esac

echo ""
echo "======================================"
echo "  ???????"
echo "======================================"
