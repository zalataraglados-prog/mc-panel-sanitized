#!/bin/bash
set -e

echo "======================================"
echo "  Minecraft Multi-Instance Deployer"
echo "======================================"

# ------------------------------
# Must run as root
# ------------------------------
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root: sudo bash install.sh"
  exit 1
fi

# ------------------------------
# Check git
# ------------------------------
if ! command -v git &> /dev/null; then
  echo "[INFO] Installing git..."
  apt update && apt install -y git
fi

if ! command -v curl &> /dev/null; then
  echo "[WARN] curl not found; rule downloads may fail."
fi

INSTALL_DIR="/opt/mc-panel-sanitized"
BRANCH="demon1.1"

# ------------------------------
# Clone / update demon1.1 branch
# ------------------------------
if [ ! -d "$INSTALL_DIR" ]; then
  echo "[INFO] Cloning repo ($BRANCH)..."
  git clone -b "$BRANCH" --single-branch \
    https://github.com/zalataraglados-prog/mc-panel-sanitized.git \
    "$INSTALL_DIR"
else
  echo "[INFO] Repo exists, updating ($BRANCH)..."
  cd "$INSTALL_DIR"
  git fetch
  git checkout "$BRANCH"
  git pull
fi

# ------------------------------
# Interactive Claims builder
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
  PLAN_OUTPUT=$(python3 -m deploy.cli plan \
    --import-string "$IMPORT_STRING")
  echo "$PLAN_OUTPUT"
  LEVEL=$(echo "$PLAN_OUTPUT" | sed -n 's/^Level:[[:space:]]*//p' | head -n 1)
  case "$LEVEL" in
    block)
      echo "[INFO] Review blocked. Execution plan not generated."
      exit 1
      ;;
    warn)
      CONFIRM=$(read_tty "Review contains warnings. Continue? [y/N] ")
      case "$CONFIRM" in
        y|Y) echo "[INFO] Warnings accepted. Generating execution plan..." ;;
        *) echo "[INFO] Operation canceled."; exit 0 ;;
      esac
      ;;
    *)
      echo "[INFO] Review passed. Generating execution plan..."
      ;;
  esac

  python3 -m deploy.cli apply \
    --import-string "$IMPORT_STRING" \
    --dry-run

  echo ""
  echo "Reusable claims string:"
  echo "$IMPORT_STRING"
  echo ""
  echo "[INFO] Execution plan complete (dry-run only)."
  exit 0
fi

cd "$INSTALL_DIR"

echo ""
VERSION=$(read_tty "Minecraft version (e.g. 1.21.4): ")
if [ -z "$VERSION" ]; then
  VERSION="1.21.4"
fi

echo ""
echo "Select Minecraft edition:"
echo "1) Java Edition"
echo "2) Bedrock Edition"
EDITION_CHOICE=$(read_tty "Enter [1-2]: ")

case "$EDITION_CHOICE" in
  2) EDITION="bedrock" ;;
  *) EDITION="java" ;;
esac

if [ "$EDITION" = "bedrock" ]; then
  echo "[INFO] Selected: Bedrock Edition"
  echo ""
  echo "Sorry, this deployer currently supports Java Edition only."
  echo "Bedrock execution is not implemented yet."
  exit 0
fi

echo ""
echo "Select profile:"
echo "1) beginner"
echo "2) normal (default)"
echo "3) advanced"
PROFILE_CHOICE=$(read_tty "Enter [1-3]: ")

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

MEMORY=$(read_tty "Memory (e.g. 2G / 4G): ")
VIEW_DISTANCE=$(read_tty "View distance (recommend 6~10): ")

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
    echo "[INFO] Review blocked. Execution plan not generated."
    exit 1
    ;;
  warn)
    CONFIRM=$(read_tty "Review contains warnings. Continue? [y/N] ")
    case "$CONFIRM" in
      y|Y) echo "[INFO] Warnings accepted. Generating execution plan..." ;;
      *) echo "[INFO] Deployment canceled."; exit 0 ;;
    esac
    ;;
  *)
    echo "[INFO] Review passed. Generating execution plan..."
    ;;
esac

python3 -m deploy.cli apply \
  --version "$VERSION" \
  --profile "$PROFILE" \
  --set edition="$EDITION" \
  --set stack.type="$STACK_TYPE" \
  --set runtime.java="$RUNTIME_JAVA" \
  --set docker.env.MEMORY="$MEMORY" \
  --set minecraft.view_distance="$VIEW_DISTANCE" \
  --dry-run

echo ""
echo "======================================"
echo "  Execution plan generated (dry-run)"
echo "======================================"
