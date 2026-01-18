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
# Ensure dependencies
# ------------------------------
if command -v apt-get >/dev/null 2>&1; then
  echo "[INFO] Checking system dependencies..."
  apt-get update
  apt-get install -y \
    ca-certificates \
    curl \
    git \
    unzip \
    python3 \
    python3-venv \
    python3-pip \
    nodejs \
    npm
  if ! command -v docker >/dev/null 2>&1; then
    echo "[INFO] Installing docker..."
    apt-get install -y docker.io
    if ! apt-get install -y docker-compose-plugin; then
      echo "[WARN] docker-compose-plugin not found; falling back to docker-compose."
      apt-get install -y docker-compose
    fi
    systemctl enable --now docker || true
  fi
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

# Ensure base instance directory exists for preconditions
mkdir -p /opt/mc-instances

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

# ------------------------------
# Language selection
# ------------------------------
LANGUAGE=$(read_tty "Select language / 选择语言 [1=EN, 2=中文]: ")
case "$LANGUAGE" in
  2) LANGUAGE="zh" ;;
  *) LANGUAGE="en" ;;
esac

msg() {
  local key="$1"
  case "$LANGUAGE" in
    zh)
      case "$key" in
        panel_maintenance) echo "面板维护（已有实例）：" ;;
        panel_install) echo "1) 为已有实例安装面板" ;;
        panel_uninstall) echo "2) 卸载已有实例面板" ;;
        panel_continue) echo "回车继续正常部署。" ;;
        panel_prompt) echo "输入 [1-2] 或留空：" ;;
        instances) echo "可用实例：" ;;
        instance_dir) echo "实例目录（可选，用于查端口）：" ;;
        import_string) echo "粘贴配置串（回车跳过）：" ;;
        import_mode) echo "导入方式：1) 粘贴配置串 2) 从文件导入（回车跳过）" ;;
        import_file) echo "配置串文件路径：" ;;
        import_file_missing) echo "[WARN] 文件不存在或不可读，将改为粘贴输入。" ;;
        import_list_header) echo "已导入配置（编号）：" ;;
        import_edit_prompt) echo "是否修改导入配置？输入行号（逗号分隔），回车跳过：" ;;
        import_confirm_prompt) echo "输入 sure 确认修改，回车跳过：" ;;
        import_value_prompt) echo "设置新值" ;;
        panel_install_prompt) echo "安装 Web 面板？[y/N] " ;;
        panel_port_prompt) echo "面板端口 [默认: 15000]: " ;;
        inventory_menu) echo "背包插件（可选）：" ;;
        inventory_url_prompt) echo "背包插件下载地址 [默认]：" ;;
        inventory_url_required) echo "背包插件下载地址（必填）：" ;;
        map_port_prompt) echo "地图插件端口 [默认: " ;;
        map_render_prompt) echo "地图渲染间隔（分钟）[默认: 5]: " ;;
        java_override) echo "是否覆盖 Java 运行时？[y/N] " ;;
        java_select) echo "选择 Java 版本：" ;;
        memory_prompt) echo "内存（例如 2G / 4G）：" ;;
        expected_players_prompt) echo "预期在线人数（可选）：" ;;
        version_menu) echo "选择 Minecraft 版本：" ;;
        version_custom) echo "自定义版本号：" ;;
        edition_menu) echo "选择 Minecraft 版本类型：" ;;
        edition_java) echo "1) Java 版" ;;
        edition_bedrock) echo "2) Bedrock 版" ;;
        bedrock_notice) echo "当前仅支持 Java 版，Bedrock 暂未实现。" ;;
        bedrock_detail) echo "Bedrock 执行层尚未实现。" ;;
        profile_menu) echo "选择配置档位：" ;;
        profile_beginner) echo "1) 新手" ;;
        profile_normal) echo "2) 标准（默认）" ;;
        profile_advanced) echo "3) 高级" ;;
        map_menu) echo "地图插件（可选）：" ;;
        map_none) echo "1) 不安装" ;;
        map_dynmap) echo "2) Dynmap" ;;
        map_bluemap) echo "3) BlueMap" ;;
        map_url_prompt) echo "地图插件下载地址 [默认]：" ;;
        map_url_fail) echo "[WARN] 下载地址不可达，请重试或选择不安装。" ;;
        plan_run) echo "[INFO] 正在执行 plan..." ;;
        plan_block) echo "[INFO] 被阻拦，可调整参数后重试。" ;;
        plan_warn) echo "存在警告，是否继续？[y/N] " ;;
        plan_ok) echo "[INFO] Review 通过，生成执行计划..." ;;
        edit_params) echo "调整参数（key=value，空行结束）：" ;;
        frontend_missing) echo "[WARN] 缺少 frontend/dist，面板需要构建。" ;;
        frontend_build_now) echo "是否现在构建前端？[y/N] " ;;
        frontend_build_skip) echo "[WARN] 已跳过前端构建，面板可能无法启动。" ;;
        npm_missing) echo "[WARN] 未检测到 npm，请安装 Node.js 后再构建。" ;;
        review_blocked) echo "[INFO] Review 被阻拦，可调整参数后重试。" ;;
        review_still_block) echo "[INFO] 仍被阻拦，已退出。" ;;
        review_canceled) echo "[INFO] 已取消。" ;;
        *) echo "$key" ;;
      esac
      ;;
    *)
      case "$key" in
        panel_maintenance) echo "Panel maintenance (existing instance):" ;;
        panel_install) echo "1) Install panel for an existing instance" ;;
        panel_uninstall) echo "2) Uninstall panel from an existing instance" ;;
        panel_continue) echo "Enter to continue normal deployment." ;;
        panel_prompt) echo "Enter [1-2] or blank: " ;;
        instances) echo "Available instances:" ;;
        instance_dir) echo "Instance dir (optional, for panel port lookup): " ;;
        import_string) echo "Paste claims string (or press Enter to continue): " ;;
        import_mode) echo "Import mode: 1) Paste string 2) From file (Enter to skip)" ;;
        import_file) echo "Claims file path: " ;;
        import_file_missing) echo "[WARN] File not found or not readable; falling back to paste." ;;
        import_list_header) echo "Imported config (indexed):" ;;
        import_edit_prompt) echo "Edit imported config? Enter line numbers (comma-separated) or Enter to skip: " ;;
        import_confirm_prompt) echo "Type sure to confirm edits, or Enter to skip: " ;;
        import_value_prompt) echo "Set new value" ;;
        panel_install_prompt) echo "Install Web Panel? [y/N] " ;;
        panel_port_prompt) echo "Panel port [default: 15000]: " ;;
        inventory_menu) echo "Inventory plugin (optional):" ;;
        inventory_url_prompt) echo "Inventory plugin download URL [default]: " ;;
        inventory_url_required) echo "Inventory plugin download URL (required): " ;;
        map_port_prompt) echo "Map plugin port [default: " ;;
        map_render_prompt) echo "Map render interval (minutes) [default: 5]: " ;;
        java_override) echo "Override Java runtime? [y/N] " ;;
        java_select) echo "Select Java runtime:" ;;
        memory_prompt) echo "Memory (e.g. 2G / 4G): " ;;
        expected_players_prompt) echo "Expected players (optional): " ;;
        version_menu) echo "Select Minecraft version:" ;;
        version_custom) echo "Custom version: " ;;
        edition_menu) echo "Select Minecraft edition:" ;;
        edition_java) echo "1) Java Edition" ;;
        edition_bedrock) echo "2) Bedrock Edition" ;;
        bedrock_notice) echo "Sorry, this deployer currently supports Java Edition only." ;;
        bedrock_detail) echo "Bedrock execution is not implemented yet." ;;
        profile_menu) echo "Select profile:" ;;
        profile_beginner) echo "1) beginner" ;;
        profile_normal) echo "2) normal (default)" ;;
        profile_advanced) echo "3) advanced" ;;
        map_menu) echo "Map plugin (optional):" ;;
        map_none) echo "1) none" ;;
        map_dynmap) echo "2) Dynmap" ;;
        map_bluemap) echo "3) BlueMap" ;;
        map_url_prompt) echo "Map plugin URL [default]: " ;;
        map_url_fail) echo "[WARN] URL unreachable; retry or choose none." ;;
        plan_run) echo "[INFO] Running plan..." ;;
        plan_block) echo "[INFO] Review blocked. You can adjust params and retry." ;;
        plan_warn) echo "Review contains warnings. Continue? [y/N] " ;;
        plan_ok) echo "[INFO] Review passed. Generating execution plan..." ;;
        edit_params) echo "Adjust params (key=value, blank to finish): " ;;
        frontend_missing) echo "[WARN] frontend/dist not found. Panel will require a frontend build." ;;
        frontend_build_now) echo "Build frontend now? [y/N] " ;;
        frontend_build_skip) echo "[WARN] Skipped frontend build. Panel service may fail until built." ;;
        npm_missing) echo "[WARN] npm not found. Install Node.js then run npm install && npm run build." ;;
        review_blocked) echo "[INFO] Review blocked. You can adjust params and retry." ;;
        review_still_block) echo "[INFO] Review still blocked. Exiting." ;;
        review_canceled) echo "[INFO] Operation canceled." ;;
        *) echo "$key" ;;
      esac
      ;;
  esac
}

choice_prompt() {
  local range="$1"
  if [ "$LANGUAGE" = "zh" ]; then
    echo "输入 [${range}]："
  else
    echo "Enter [${range}]: "
  fi
}

# ------------------------------
# Optional panel maintenance mode
# ------------------------------
echo ""
echo "$(msg panel_maintenance)"
echo "$(msg panel_install)"
echo "$(msg panel_uninstall)"
echo "$(msg panel_continue)"
PANEL_MAINT=$(read_tty "$(msg panel_prompt)")

if [ "$PANEL_MAINT" = "1" ] || [ "$PANEL_MAINT" = "2" ]; then
  echo ""
  echo "[INFO] $(msg instances)"
  python3 -m deploy.cli instances || true
  INSTANCE_DIR=$(read_tty "$(msg instance_dir)")
  if [ "$PANEL_MAINT" = "1" ]; then
    BUILD_PANEL="y"
    if [ -f "$INSTALL_DIR/frontend/dist/index.html" ]; then
      BUILD_PANEL=$(read_tty "Frontend already built. Rebuild? [y/N] ")
    fi
    if [ "$BUILD_PANEL" = "y" ] || [ "$BUILD_PANEL" = "Y" ]; then
      python3 -m deploy.cli panel install ${INSTANCE_DIR:+--instance-dir "$INSTANCE_DIR"}
    else
      python3 -m deploy.cli panel install ${INSTANCE_DIR:+--instance-dir "$INSTANCE_DIR"} --no-build
    fi
  else
    python3 -m deploy.cli panel uninstall ${INSTANCE_DIR:+--instance-dir "$INSTANCE_DIR"}
  fi
  exit 0
fi

echo ""
IMPORT_MODE=$(read_tty "$(msg import_mode)")
IMPORT_MODE="${IMPORT_MODE//$'\r'/}"
IMPORT_MODE="$(echo "$IMPORT_MODE" | xargs)"
case "$IMPORT_MODE" in
  2)
    IMPORT_FILE=$(read_tty "$(msg import_file)")
    IMPORT_FILE="${IMPORT_FILE//$'\r'/}"
    if [ -n "$IMPORT_FILE" ] && [ -f "$IMPORT_FILE" ]; then
      IMPORT_STRING=$(cat "$IMPORT_FILE")
    else
      echo "$(msg import_file_missing)"
      IMPORT_STRING=$(read_tty "$(msg import_string)")
    fi
    ;;
  1|"")
    IMPORT_STRING=$(read_tty "$(msg import_string)")
    ;;
  *)
    IMPORT_STRING=$(read_tty "$(msg import_string)")
    ;;
esac
IMPORT_STRING="$(echo "$IMPORT_STRING" | tr -d '\r\n\t')"
export IMPORT_STRING
cd "$INSTALL_DIR"
IMPORT_FORMAT=""
IMPORT_VERSION=""
IMPORT_PRESENT=""
if [ -n "$IMPORT_STRING" ]; then
  IMPORT_PRESENT="1"
  IMPORT_FORMAT=$(python3 - <<'PY'
import os
from deploy.claims_codec import is_compact_string, peek_version
from deploy.claims_codec.minimal import is_minimal_string, peek_version as peek_min
value = os.environ.get("IMPORT_STRING", "")
if is_compact_string(value):
    print("compact")
elif is_minimal_string(value):
    print("min")
else:
    print("")
PY
)
  IMPORT_VERSION=$(python3 - <<'PY'
import os
from deploy.claims_codec import is_compact_string, peek_version
from deploy.claims_codec.minimal import is_minimal_string, peek_version as peek_min
value = os.environ.get("IMPORT_STRING", "")
if is_compact_string(value):
    print(peek_version(value))
elif is_minimal_string(value):
    print(peek_min(value))
else:
    print("")
PY
  )
  if [ "$IMPORT_FORMAT" != "min" ]; then
    IMPORT_STRING="${IMPORT_STRING// /}"
  fi
fi
export MC_PANEL_ROOT="$INSTALL_DIR"
export MC_PANEL_LANG="$LANGUAGE"
export PYTHONIOENCODING="utf-8"
export MC_PANEL_LOG_DIR="$INSTALL_DIR/logs"
export MC_PANEL_LOG_BRANCH="logs"
export MC_PANEL_LOG_WORKTREE="$INSTALL_DIR/.logs-worktree"
export MC_PANEL_LOG_PUSH="1"

echo ""
VERSIONS_FILE="/tmp/mc_versions.txt"
python3 - <<'PY' > "$VERSIONS_FILE"
import json
import re
import sys
import urllib.request

url = "https://api.github.com/repos/zalataraglados-prog/vanilla_catalog/contents/catalog"
fallback = [
    "1.21.11",
    "1.21.4",
    "1.20.6",
    "1.20.5",
    "1.20.4",
    "1.20.3",
    "1.20.2",
    "1.20.1",
    "1.20",
    "1.19.4",
    "1.19.3",
    "1.19.2",
    "1.19.1",
    "1.19",
    "1.18.2",
    "1.18.1",
    "1.18",
    "1.17.1",
    "1.17",
    "1.16.5",
    "1.16.4",
    "1.16.3",
    "1.16.2",
    "1.16.1",
    "1.16",
    "1.15.2",
    "1.15.1",
    "1.15",
    "1.14.4",
    "1.14.3",
    "1.14.2",
    "1.14.1",
    "1.14",
    "1.13.2",
    "1.13.1",
    "1.13",
    "1.12.2",
    "1.12.1",
    "1.12",
    "1.11.2",
    "1.11.1",
    "1.11",
    "1.10.2",
    "1.10.1",
    "1.10",
    "1.9.4",
    "1.9.3",
    "1.9.2",
    "1.9.1",
    "1.9",
    "1.8.9",
    "1.8.8",
    "1.8.7",
    "1.8.6",
    "1.8.5",
    "1.8.4",
    "1.8.3",
    "1.8.2",
    "1.8.1",
    "1.8",
    "1.7.10",
    "1.7.9",
    "1.7.8",
    "1.7.7",
    "1.7.6",
    "1.7.5",
    "1.7.4",
    "1.7.3",
    "1.7.2",
    "1.7.1",
    "1.7",
    "1.6.4",
    "1.6.3",
    "1.6.2",
    "1.6.1",
    "1.6",
    "1.5.2",
    "1.5.1",
    "1.5",
    "1.4.7",
    "1.4.6",
    "1.4.5",
    "1.4.4",
    "1.4.3",
    "1.4.2",
    "1.4.1",
    "1.4",
    "1.3.2",
    "1.3.1",
    "1.3",
    "1.2.5",
    "1.2.4",
    "1.2.3",
    "1.2.2",
    "1.2.1",
    "1.2",
    "1.1",
    "1.0",
]

def version_key(v: str):
    parts = v.split(".")
    nums = []
    for part in parts:
        try:
            nums.append(int(part))
        except ValueError:
            nums.append(0)
    return tuple(nums + [0] * (3 - len(nums)))

try:
    with urllib.request.urlopen(url, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    versions = []
    for item in data:
        name = item.get("name", "")
        match = re.match(r"vanilla_(.+)\\.json$", name)
        if match:
            versions.append(match.group(1))
    versions = sorted(set(versions), key=version_key, reverse=True)
    if not versions:
        versions = sorted(fallback, key=version_key, reverse=True)
except Exception:
    versions = sorted(fallback, key=version_key, reverse=True)

for v in versions:
    print(v)
PY

mapfile -t VERSIONS < "$VERSIONS_FILE"
if [ "${#VERSIONS[@]}" -eq 0 ]; then
  VERSIONS=("1.21.4")
fi

if [ -n "$IMPORT_VERSION" ]; then
  VERSION="$IMPORT_VERSION"
else
  echo "$(msg version_menu)"
  i=1
  for v in "${VERSIONS[@]}"; do
    echo "${i}) ${v}"
    i=$((i + 1))
  done
  echo "${i}) custom"
  VERSION_CHOICE=$(read_tty "$(choice_prompt 1-${i})")
  VERSION_CHOICE="${VERSION_CHOICE//$'\r'/}"
  VERSION_CHOICE="$(echo "$VERSION_CHOICE" | xargs)"
  FROM_CUSTOM="0"
  if [[ "$VERSION_CHOICE" =~ ^[0-9]+$ ]] && [ "$VERSION_CHOICE" -ge 1 ] && [ "$VERSION_CHOICE" -le "${#VERSIONS[@]}" ]; then
    VERSION="${VERSIONS[$((VERSION_CHOICE - 1))]}"
  elif [[ "$VERSION_CHOICE" =~ ^[0-9]+$ ]] && [ "$VERSION_CHOICE" -eq "${i}" ]; then
    FROM_CUSTOM="1"
    VERSION=""
  else
    VERSION="${VERSIONS[0]}"
  fi
  if [ "$FROM_CUSTOM" = "1" ]; then
    VERSION=$(read_tty "$(msg version_custom)")
    VERSION="${VERSION//$'\r'/}"
    VERSION="$(echo "$VERSION" | xargs)"
    while [ -n "$VERSION" ] && ! [[ "$VERSION" =~ ^[0-9]+\\.[0-9]+(\\.[0-9]+)?$ ]]; do
      VERSION=$(read_tty "$(msg version_custom)")
      VERSION="${VERSION//$'\r'/}"
      VERSION="$(echo "$VERSION" | xargs)"
    done
  fi
  if [ -z "$VERSION" ]; then
    VERSION="${VERSIONS[0]}"
  fi
fi
export VERSION

if [ -n "$IMPORT_PRESENT" ]; then
  EDITION="java"
  PROFILE="advanced"
  SKIP_PROFILE="1"
else
  echo ""
  echo "$(msg edition_menu)"
  echo "$(msg edition_java)"
  echo "$(msg edition_bedrock)"
  EDITION_CHOICE=$(read_tty "$(choice_prompt 1-2)")

  case "$EDITION_CHOICE" in
    2) EDITION="bedrock" ;;
    *) EDITION="java" ;;
  esac

  if [ "$EDITION" = "bedrock" ]; then
    echo ""
    echo "[INFO] $(msg bedrock_notice)"
    echo "$(msg bedrock_detail)"
    exit 0
  fi

  echo ""
  echo "$(msg profile_menu)"
  echo "$(msg profile_beginner)"
  echo "$(msg profile_normal)"
  echo "$(msg profile_advanced)"
  PROFILE_CHOICE=$(read_tty "$(choice_prompt 1-3)")

  case "$PROFILE_CHOICE" in
    1) PROFILE="beginner" ;;
    3) PROFILE="advanced" ;;
    *) PROFILE="normal" ;;
  esac
fi

PARAMS_JSON="/tmp/claims_params.json"
export PARAMS_JSON

python3 - <<'PY'
import json
import os
from deploy.loader import load_rules_bundle
path = os.environ.get("PARAMS_JSON")
version = os.environ.get("VERSION")
base_url = os.environ.get("RULES_BASE_URL")
rules_ref = os.environ.get("RULES_REF")
params = {}
if version:
    bundle = load_rules_bundle(version, base_url=base_url, rules_ref=rules_ref)
    catalog = bundle.get("catalog", {})
    for section in ("server_properties", "gamerule"):
        entries = catalog.get(section, {}).get("entries", {})
        for key, meta in entries.items():
            if "default" in meta:
                params[key] = meta["default"]
with open(path, "w", encoding="utf-8") as handle:
    json.dump(params, handle)
PY

while [ -n "$IMPORT_STRING" ]; do
  export IMPORT_STRING
  if ! python3 - <<'PY'
import json
import os
from deploy.claims_codec import decode_auto
from deploy.loader import load_rules_bundle
path = os.environ["PARAMS_JSON"]
with open(path, "r", encoding="utf-8") as handle:
    params = json.load(handle)
try:
    version = os.environ.get("VERSION")
    bundle = load_rules_bundle(version) if version else {}
    catalog = bundle.get("catalog", {})
    decoded = decode_auto(os.environ["IMPORT_STRING"], catalog)
except Exception as exc:
    print(f"[ERROR] ??????????{exc}")
    raise SystemExit(2)
params.update(decoded)
with open(path, "w", encoding="utf-8") as handle:
    json.dump(params, handle)
PY
  then
    echo "[ERROR] ?????????????????????"
    IMPORT_STRING=$(read_tty "$(msg import_string)")
    IMPORT_STRING="$(echo "$IMPORT_STRING" | tr -d '\r\n\t')"
    if [ -z "$IMPORT_STRING" ]; then
      continue
    fi
    IMPORT_FORMAT=$(python3 - <<'PY'
import os
from deploy.claims_codec import is_compact_string, peek_version
from deploy.claims_codec.minimal import is_minimal_string, peek_version as peek_min
value = os.environ.get("IMPORT_STRING", "")
if is_compact_string(value):
    print("compact")
elif is_minimal_string(value):
    print("min")
else:
    print("")
PY
)
    if [ "$IMPORT_FORMAT" != "min" ]; then
      IMPORT_STRING="${IMPORT_STRING// /}"
    fi
    continue
  fi
  IMPORT_PRESENT="1"
  echo ""
  echo "$(msg import_list_header)"
  python3 - <<'PY'
import json
import os
with open(os.environ["PARAMS_JSON"], "r", encoding="utf-8") as handle:
    params = json.load(handle)
items = sorted(params.items(), key=lambda item: item[0])
for idx, (key, value) in enumerate(items, start=1):
    print(f"{idx}\t{key}\t{value}")
PY
  PARAMS_JSON_BAK="/tmp/claims_params.bak"
  cp "$PARAMS_JSON" "$PARAMS_JSON_BAK"
  EDIT_LINES=$(read_tty "$(msg import_edit_prompt)")
  if [ -n "$EDIT_LINES" ]; then
    EDIT_LINES="${EDIT_LINES// /}"
    IFS=',' read -r -a LINE_ITEMS <<< "$EDIT_LINES"
    for line in "${LINE_ITEMS[@]}"; do
      if ! [[ "$line" =~ ^[0-9]+$ ]]; then
        echo "[WARN] Invalid line number: ${line}"
        continue
      fi
      KEY=$(LINE_NO="$line" python3 - <<'PY'
import json
import os
line = int(os.environ["LINE_NO"])
with open(os.environ["PARAMS_JSON"], "r", encoding="utf-8") as handle:
    params = json.load(handle)
items = sorted(params.items(), key=lambda item: item[0])
if line < 1 or line > len(items):
    print("")
else:
    print(items[line-1][0])
PY
      )
      if [ -z "$KEY" ]; then
        echo "[WARN] Line out of range: ${line}"
        continue
      fi
      CURRENT=$(PARAM_KEY="$KEY" get_param "$KEY")
      VALUE=$(read_tty "$(msg import_value_prompt) ${KEY} [${CURRENT}]: ")
      if [ -z "$VALUE" ]; then
        continue
      fi
      PARAM_KEY="$KEY" PARAM_VALUE="$VALUE" set_param "$KEY" "$VALUE"
    done
    CONFIRM_EDIT=$(read_tty "$(msg import_confirm_prompt)")
    if [ "$CONFIRM_EDIT" != "sure" ]; then
      cp "$PARAMS_JSON_BAK" "$PARAMS_JSON"
    fi
  fi
  SKIP_PROMPTS="1"
  break
done

get_param() {
  local key="$1"
  python3 - <<'PY'
import json
import os
key = os.environ["PARAM_KEY"]
with open(os.environ["PARAMS_JSON"], "r", encoding="utf-8") as handle:
    data = json.load(handle)
print(data.get(key, ""))
PY
}

set_param() {
  local key="$1"
  local value="$2"
  python3 - <<'PY'
import json
import os
key = os.environ["PARAM_KEY"]
value = os.environ["PARAM_VALUE"]
with open(os.environ["PARAMS_JSON"], "r", encoding="utf-8") as handle:
    data = json.load(handle)
data[key] = value
with open(os.environ["PARAMS_JSON"], "w", encoding="utf-8") as handle:
    json.dump(data, handle)
PY
}

PANEL_ENABLED=$(PARAM_KEY="panel.enable" get_param "panel.enable")
if [ -z "$PANEL_ENABLED" ] && [ -z "$IMPORT_PRESENT" ]; then
  echo ""
  PANEL_CHOICE=$(read_tty "$(msg panel_install_prompt)")
  case "$PANEL_CHOICE" in
    y|Y) PARAM_KEY="panel.enable" PARAM_VALUE="true" set_param "panel.enable" "true" ;;
    *) : ;;
  esac
fi

PANEL_PORT_EXISTS=$(PARAM_KEY="panel.port" get_param "panel.port")
PANEL_ENABLED=$(PARAM_KEY="panel.enable" get_param "panel.enable")
if [ -z "$PANEL_PORT_EXISTS" ] && [ "$PANEL_ENABLED" = "true" ] && [ -z "$IMPORT_PRESENT" ]; then
  PANEL_PORT=$(read_tty "$(msg panel_port_prompt)")
  if [ -z "$PANEL_PORT" ]; then
    PANEL_PORT="15000"
  fi
  PARAM_KEY="panel.port" PARAM_VALUE="$PANEL_PORT" set_param "panel.port" "$PANEL_PORT"
fi

if [ "$PANEL_ENABLED" = "true" ]; then
  if ! python3 -m venv --help >/dev/null 2>&1; then
    apt update && apt install -y python3-venv
  fi
fi

if [ "$PANEL_ENABLED" = "true" ]; then
  if [ ! -f "$INSTALL_DIR/frontend/dist/index.html" ]; then
    echo ""
    echo "$(msg frontend_missing)"
    if ! command -v npm >/dev/null 2>&1; then
      echo "$(msg npm_missing)"
      if command -v apt >/dev/null 2>&1; then
        apt update && apt install -y nodejs npm
      fi
    fi
    if command -v npm >/dev/null 2>&1; then
      if [ -z "$IMPORT_PRESENT" ]; then
        BUILD_PANEL=$(read_tty "$(msg frontend_build_now)")
        if [ "$BUILD_PANEL" = "y" ] || [ "$BUILD_PANEL" = "Y" ]; then
          (cd "$INSTALL_DIR/frontend" && npm install && npm run build)
        else
          echo "$(msg frontend_build_skip)"
        fi
      else
        (cd "$INSTALL_DIR/frontend" && npm install && npm run build)
      fi
    fi
  fi
fi

MAP_PLUGIN_EXISTS=$(PARAM_KEY="map.plugin" get_param "map.plugin")
if [ -z "$MAP_PLUGIN_EXISTS" ] && [ -z "$IMPORT_PRESENT" ]; then
  echo ""
  echo "$(msg map_menu)"
  echo "$(msg map_none)"
  echo "$(msg map_dynmap)"
  echo "$(msg map_bluemap)"
  PLUGIN_CHOICE=$(read_tty "$(choice_prompt 1-3)")
  while true; do
    case "$PLUGIN_CHOICE" in
      2) MAP_PLUGIN="dynmap" ;;
      3) MAP_PLUGIN="bluemap" ;;
      *) MAP_PLUGIN="" ;;
    esac
    if [ -z "$MAP_PLUGIN" ]; then
      break
    fi
    DEFAULT_MAP_URL=""
    if [ "$MAP_PLUGIN" = "dynmap" ]; then
      DEFAULT_MAP_URL="https://dynmap.us/builds/dynmap/Dynmap-HEAD-spigot.jar"
    elif [ "$MAP_PLUGIN" = "bluemap" ]; then
      DEFAULT_MAP_URL="https://github.com/BlueMap-Minecraft/BlueMap/releases/latest/download/bluemap-5.15-spigot.jar"
    fi
    MAP_URL=$(read_tty "$(msg map_url_prompt) ${DEFAULT_MAP_URL} ")
    if [ -z "$MAP_URL" ]; then
      MAP_URL="$DEFAULT_MAP_URL"
    fi
    if [ -n "$MAP_URL" ] && command -v curl >/dev/null 2>&1; then
      if ! curl -fsSLI --max-time 10 "$MAP_URL" >/dev/null; then
        echo "$(msg map_url_fail)"
        PLUGIN_CHOICE=$(read_tty "$(choice_prompt 1-3)")
        continue
      fi
    fi
    PARAM_KEY="map.plugin" PARAM_VALUE="$MAP_PLUGIN" set_param "map.plugin" "$MAP_PLUGIN"
    if [ -n "$MAP_URL" ]; then
      PARAM_KEY="map.plugin_url" PARAM_VALUE="$MAP_URL" set_param "map.plugin_url" "$MAP_URL"
    fi
    break
  done
fi

MAP_PORT_EXISTS=$(PARAM_KEY="map.plugin_port" get_param "map.plugin_port")
if [ -z "$MAP_PORT_EXISTS" ] && [ -z "$IMPORT_PRESENT" ]; then
  if [ "$MAP_PLUGIN" = "dynmap" ] || [ "$MAP_PLUGIN_EXISTS" = "dynmap" ]; then
    DEFAULT_MAP_PORT="8123"
  elif [ "$MAP_PLUGIN" = "bluemap" ] || [ "$MAP_PLUGIN_EXISTS" = "bluemap" ]; then
    DEFAULT_MAP_PORT="8100"
  else
    DEFAULT_MAP_PORT=""
  fi
  if [ -n "$DEFAULT_MAP_PORT" ]; then
    MAP_PORT=$(read_tty "$(msg map_port_prompt)${DEFAULT_MAP_PORT}]: ")
    if [ -z "$MAP_PORT" ]; then
      MAP_PORT="$DEFAULT_MAP_PORT"
    fi
    PARAM_KEY="map.plugin_port" PARAM_VALUE="$MAP_PORT" set_param "map.plugin_port" "$MAP_PORT"
  fi
fi

MAP_RENDER_EXISTS=$(PARAM_KEY="map.render_interval" get_param "map.render_interval")
if [ -z "$MAP_RENDER_EXISTS" ] && [ -z "$IMPORT_PRESENT" ]; then
  if [ "$MAP_PLUGIN" = "dynmap" ] || [ "$MAP_PLUGIN_EXISTS" = "dynmap" ] || [ "$MAP_PLUGIN" = "bluemap" ] || [ "$MAP_PLUGIN_EXISTS" = "bluemap" ]; then
    MAP_RENDER=$(read_tty "$(msg map_render_prompt)")
    if [ -z "$MAP_RENDER" ]; then
      MAP_RENDER="5"
    fi
    PARAM_KEY="map.render_interval" PARAM_VALUE="$MAP_RENDER" set_param "map.render_interval" "$MAP_RENDER"
  fi
fi

INVENTORY_PLUGIN_EXISTS=$(PARAM_KEY="inventory.plugin" get_param "inventory.plugin")
INVENTORY_PLUGIN=""
if [ -z "$INVENTORY_PLUGIN_EXISTS" ] && [ -z "$IMPORT_PRESENT" ]; then
  echo ""
  echo "$(msg inventory_menu)"
  echo "1) none"
  echo "2) InvSee++ (recommended)"
  echo "3) OpenInv"
  INV_PLUGIN_CHOICE=$(read_tty "$(choice_prompt 1-3)")
  case "$INV_PLUGIN_CHOICE" in
    2) INVENTORY_PLUGIN="invsee" ;;
    3) INVENTORY_PLUGIN="openinv" ;;
    *) INVENTORY_PLUGIN="" ;;
  esac
  if [ -n "$INVENTORY_PLUGIN" ]; then
    DEFAULT_INV_URL=""
    if [ "$INVENTORY_PLUGIN" = "invsee" ]; then
      DEFAULT_INV_URL="https://raw.githubusercontent.com/zalataraglados-prog/vanilla_catalog/main/deps/plugins/invsee/InvSeePlusPlus.jar"
    elif [ "$INVENTORY_PLUGIN" = "openinv" ]; then
      DEFAULT_INV_URL="https://raw.githubusercontent.com/zalataraglados-prog/vanilla_catalog/main/deps/plugins/openinv/OpenInv.jar"
    fi
    if [ -n "$DEFAULT_INV_URL" ]; then
      INVENTORY_URL=$(read_tty "$(msg inventory_url_prompt) ${DEFAULT_INV_URL} ")
      if [ -z "$INVENTORY_URL" ]; then
        INVENTORY_URL="$DEFAULT_INV_URL"
      fi
    else
      INVENTORY_URL=$(read_tty "$(msg inventory_url_required)")
    fi
    if [ -n "$INVENTORY_URL" ]; then
      PARAM_KEY="inventory.plugin" PARAM_VALUE="$INVENTORY_PLUGIN" set_param "inventory.plugin" "$INVENTORY_PLUGIN"
      PARAM_KEY="inventory.plugin_url" PARAM_VALUE="$INVENTORY_URL" set_param "inventory.plugin_url" "$INVENTORY_URL"
    else
      echo "[WARN] No plugin URL provided; inventory plugin will not be installed."
      INVENTORY_PLUGIN=""
    fi
  fi
else
  INVENTORY_PLUGIN="$INVENTORY_PLUGIN_EXISTS"
fi

INVENTORY_URL_EXISTS=$(PARAM_KEY="inventory.plugin_url" get_param "inventory.plugin_url")
if [ -n "$INVENTORY_PLUGIN" ] && [ -z "$INVENTORY_URL_EXISTS" ] && [ -z "$IMPORT_PRESENT" ]; then
  DEFAULT_INV_URL=""
  if [ "$INVENTORY_PLUGIN" = "invsee" ]; then
    DEFAULT_INV_URL="https://raw.githubusercontent.com/zalataraglados-prog/vanilla_catalog/main/deps/plugins/invsee/InvSeePlusPlus.jar"
  elif [ "$INVENTORY_PLUGIN" = "openinv" ]; then
    DEFAULT_INV_URL="https://raw.githubusercontent.com/zalataraglados-prog/vanilla_catalog/main/deps/plugins/openinv/OpenInv.jar"
  fi
  if [ -n "$DEFAULT_INV_URL" ]; then
    INVENTORY_URL=$(read_tty "$(msg inventory_url_prompt) ${DEFAULT_INV_URL} ")
    if [ -z "$INVENTORY_URL" ]; then
      INVENTORY_URL="$DEFAULT_INV_URL"
    fi
  else
    INVENTORY_URL=$(read_tty "$(msg inventory_url_required)")
  fi
  if [ -n "$INVENTORY_URL" ]; then
    PARAM_KEY="inventory.plugin_url" PARAM_VALUE="$INVENTORY_URL" set_param "inventory.plugin_url" "$INVENTORY_URL"
  else
    echo "[WARN] No plugin URL provided; inventory plugin will not be installed."
  fi
fi

MAP_FILE_EXISTS=$(PARAM_KEY="map.file" get_param "map.file")
if [ -z "$MAP_FILE_EXISTS" ] && [ -z "$IMPORT_PRESENT" ]; then
  MAP_FILE=$(read_tty "Optional map file (world zip/dir path): ")
  if [ -n "$MAP_FILE" ]; then
    PARAM_KEY="map.file" PARAM_VALUE="$MAP_FILE" set_param "map.file" "$MAP_FILE"
    MAP_TARGET=$(read_tty "Map target folder [default: world]: ")
    if [ -z "$MAP_TARGET" ]; then
      MAP_TARGET="world"
    fi
    PARAM_KEY="map.target" PARAM_VALUE="$MAP_TARGET" set_param "map.target" "$MAP_TARGET"
    MAP_OVERWRITE=$(read_tty "Overwrite existing world? [Y/n] ")
    case "$MAP_OVERWRITE" in
      n|N) PARAM_KEY="map.overwrite" PARAM_VALUE="false" set_param "map.overwrite" "false" ;;
      *) PARAM_KEY="map.overwrite" PARAM_VALUE="true" set_param "map.overwrite" "true" ;;
    esac
  fi
fi

echo ""
if [ -z "$IMPORT_PRESENT" ]; then
  OVERRIDE_JAVA=$(read_tty "$(msg java_override)")
else
  OVERRIDE_JAVA="n"
fi
if [ "$OVERRIDE_JAVA" = "y" ] || [ "$OVERRIDE_JAVA" = "Y" ]; then
  echo ""
  echo "$(msg java_select)"
  echo "1) auto (based on Minecraft version)"
  echo "2) 8"
  echo "3) 11"
  echo "4) 16"
  echo "5) 17"
  RUNTIME_CHOICE=$(read_tty "$(choice_prompt 1-5)")
  case "$RUNTIME_CHOICE" in
    2) RUNTIME_JAVA="8" ;;
    3) RUNTIME_JAVA="11" ;;
    4) RUNTIME_JAVA="16" ;;
    5) RUNTIME_JAVA="17" ;;
    *) RUNTIME_JAVA="auto" ;;
  esac
  PARAM_KEY="runtime.java" PARAM_VALUE="$RUNTIME_JAVA" set_param "runtime.java" "$RUNTIME_JAVA"
fi

MEMORY_EXISTS=$(PARAM_KEY="docker.env.MEMORY" get_param "docker.env.MEMORY")
if [ -z "$MEMORY_EXISTS" ] && [ -z "$IMPORT_PRESENT" ]; then
  MEMORY=$(read_tty "$(msg memory_prompt)")
  if [ -n "$MEMORY" ]; then
    PARAM_KEY="docker.env.MEMORY" PARAM_VALUE="$MEMORY" set_param "docker.env.MEMORY" "$MEMORY"
  fi
fi

EXPECTED_PLAYERS=$(PARAM_KEY="deploy.expected_players" get_param "deploy.expected_players")
if [ -z "$EXPECTED_PLAYERS" ] && [ -z "$IMPORT_PRESENT" ]; then
  EXPECTED_PLAYERS=$(read_tty "$(msg expected_players_prompt)")
  if [ -n "$EXPECTED_PLAYERS" ]; then
    PARAM_KEY="deploy.expected_players" PARAM_VALUE="$EXPECTED_PLAYERS" set_param "deploy.expected_players" "$EXPECTED_PLAYERS"
  fi
fi

if [ -z "$IMPORT_STRING" ]; then
  PARAM_KEY="edition" PARAM_VALUE="$EDITION" set_param "edition" "$EDITION"
  PARAM_KEY="stack.type" PARAM_VALUE="paper" set_param "stack.type" "paper"
fi

echo ""
echo "[INFO] Loading parameters from catalog for prompting..."
python3 - <<'PY' > /tmp/param_keys.txt
import os
from deploy.loader import load_rules_bundle

version = os.environ["VERSION"]
base_url = os.environ.get("RULES_BASE_URL")
rules_ref = os.environ.get("RULES_REF")

bundle = load_rules_bundle(version, base_url=base_url, rules_ref=rules_ref)
catalog = bundle["catalog"]
usability = bundle.get("usability", {})

def pick_default(section, key, catalog_default):
    entry = usability.get(section, {}).get("entries", {}).get(key, {})
    usage = entry.get("usability", {})
    hint = usage.get("default_hint")
    return hint if hint is not None else catalog_default

for section in ("server_properties", "gamerule"):
    entries = catalog.get(section, {}).get("entries", {})
    for key, meta in entries.items():
        default = meta.get("default")
        hint = pick_default(section, key, default)
        entry = usability.get(section, {}).get("entries", {}).get(key, {})
        usage = entry.get("usability", {})
        rec_range = usage.get("recommended_range", {})
        min_val = rec_range.get("min")
        max_val = rec_range.get("max")
        if isinstance(default, bool):
            dtype = "bool"
        elif isinstance(default, int):
            dtype = "int"
        else:
            dtype = "string"
        if dtype == "string" and hint == "string":
            hint = ""
        print(f"{key}\t{'' if hint is None else hint}\t{dtype}\t{'' if min_val is None else min_val}\t{'' if max_val is None else max_val}")
PY

if [ "$SKIP_PROMPTS" = "1" ]; then
  : 
else
  while IFS=$'\t' read -r key default_hint dtype min_val max_val; do
    existing=$(PARAM_KEY="$key" get_param "$key")
    if [ -n "$existing" ]; then
      prompt_default="$existing"
    else
      prompt_default="$default_hint"
    fi
    if [ -n "$prompt_default" ]; then
      prompt="Set ${key} [default: ${prompt_default}]: "
    else
      prompt="Set ${key} (optional): "
    fi
  value=$(read_tty "$prompt")
  if [ -z "$value" ]; then
    continue
  fi
  if [ "$dtype" = "bool" ]; then
    case "$value" in
      true|false|TRUE|FALSE|1|0) : ;;
      *) echo "[WARN] Invalid boolean for ${key}, skipping."; continue ;;
    esac
  elif [ "$dtype" = "int" ]; then
    case "$value" in
      ''|*[!0-9]*) echo "[WARN] Invalid integer for ${key}, skipping."; continue ;;
    esac
    if [ -n "$min_val" ]; then
      if [ "$value" -lt "$min_val" ]; then
        echo "[WARN] ${key} below recommended min (${min_val}), skipping."
        continue
      fi
    fi
    if [ -n "$max_val" ]; then
      if [ "$value" -gt "$max_val" ]; then
        echo "[WARN] ${key} above recommended max (${max_val}), skipping."
        continue
      fi
    fi
  fi
    PARAM_KEY="$key" PARAM_VALUE="$value" set_param "$key" "$value"
  done < /tmp/param_keys.txt
fi

CLAIMS_STRING=$(python3 - <<'PY'
import json
import os
from deploy.claims_codec.encode import encode_claims
with open(os.environ["PARAMS_JSON"], "r", encoding="utf-8") as handle:
    params = json.load(handle)
print(encode_claims(params))
PY
)

WARN_CONFIRMED="0"
while true; do
  echo ""
  echo "$(msg plan_run)"
  PLAN_OUTPUT=$(python3 -m deploy.cli plan \
    --version "$VERSION" \
    --profile "$PROFILE" \
    --import-string "$CLAIMS_STRING")
  echo "$PLAN_OUTPUT"
  LEVEL=$(echo "$PLAN_OUTPUT" | sed -n 's/^Level:[[:space:]]*//p' | head -n 1)
  if [ -z "$LEVEL" ]; then
    LEVEL=$(echo "$PLAN_OUTPUT" | sed -n 's/^级别:[[:space:]]*//p' | head -n 1)
  fi
  LEVEL="$(echo "$LEVEL" | xargs | tr 'A-Z' 'a-z')"

  case "$LEVEL" in
    block)
      echo "$(msg review_blocked)"
      echo "$(msg edit_params)"
      CHANGED="0"
      while true; do
        ENTRY=$(read_tty "")
        if [ -z "$ENTRY" ]; then
          break
        fi
        if ! echo "$ENTRY" | grep -q "="; then
          echo "[WARN] Invalid format, use key=value."
          continue
        fi
        KEY="${ENTRY%%=*}"
        VALUE="${ENTRY#*=}"
        PARAM_KEY="$KEY" PARAM_VALUE="$VALUE" set_param "$KEY" "$VALUE"
        CHANGED="1"
      done
      if [ "$CHANGED" != "1" ]; then
        continue
      fi
      CLAIMS_STRING=$(python3 - <<'PY'
import json
import os
from deploy.claims_codec.encode import encode_claims
with open(os.environ["PARAMS_JSON"], "r", encoding="utf-8") as handle:
    params = json.load(handle)
print(encode_claims(params))
PY
)
      continue
      ;;
    warn)
      CONFIRM=$(read_tty "$(msg plan_warn)")
      case "$CONFIRM" in
        y|Y) echo "$(msg plan_ok)"; WARN_CONFIRMED="1" ;;
        *) echo "$(msg review_canceled)"; exit 0 ;;
      esac
      ;;
    *)
      echo "$(msg plan_ok)"
      ;;
  esac

  if [ "$LEVEL" = "warn" ] && [ "$WARN_CONFIRMED" != "1" ]; then
    CONFIRM=$(read_tty "$(msg plan_warn)")
    case "$CONFIRM" in
      y|Y) WARN_CONFIRMED="1" ;;
      *) echo "$(msg review_canceled)"; exit 0 ;;
    esac
  fi
  break
done

APPLY_FLAGS="--apply --no-review"
if [ "$LEVEL" = "warn" ]; then
  APPLY_FLAGS="${APPLY_FLAGS} --confirm-warn"
fi

python3 -m deploy.cli apply \
  --version "$VERSION" \
  --profile "$PROFILE" \
  --import-string "$CLAIMS_STRING" \
  $APPLY_FLAGS

echo ""
echo "Reusable claims string:"
echo "$CLAIMS_STRING"
echo ""
echo "[INFO] Execution plan complete."
exit 0
