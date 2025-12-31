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

PARAMS_JSON="/tmp/claims_params.json"

python3 - <<'PY'
import json
import os
path = os.environ.get("PARAMS_JSON")
with open(path, "w", encoding="utf-8") as handle:
    json.dump({}, handle)
PY

if [ -n "$IMPORT_STRING" ]; then
  python3 - <<'PY'
import json
import os
from deploy.claims_codec.decode import decode_claims
params = decode_claims(os.environ["IMPORT_STRING"])
with open(os.environ["PARAMS_JSON"], "w", encoding="utf-8") as handle:
    json.dump(params, handle)
PY
fi

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

MAP_PLUGIN_EXISTS=$(PARAM_KEY="map.plugin" get_param "map.plugin")
if [ -z "$MAP_PLUGIN_EXISTS" ]; then
  echo ""
  echo "Map plugin (optional):"
  echo "1) none"
  echo "2) Dynmap"
  echo "3) BlueMap"
  PLUGIN_CHOICE=$(read_tty "Enter [1-3]: ")
  case "$PLUGIN_CHOICE" in
    2) MAP_PLUGIN="dynmap" ;;
    3) MAP_PLUGIN="bluemap" ;;
    *) MAP_PLUGIN="" ;;
  esac
  if [ -n "$MAP_PLUGIN" ]; then
    PARAM_KEY="map.plugin" PARAM_VALUE="$MAP_PLUGIN" set_param "map.plugin" "$MAP_PLUGIN"
  fi
fi

echo ""
OVERRIDE_JAVA=$(read_tty "Override Java runtime? [y/N] ")
if [ "$OVERRIDE_JAVA" = "y" ] || [ "$OVERRIDE_JAVA" = "Y" ]; then
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
  PARAM_KEY="runtime.java" PARAM_VALUE="$RUNTIME_JAVA" set_param "runtime.java" "$RUNTIME_JAVA"
fi

MEMORY_EXISTS=$(PARAM_KEY="docker.env.MEMORY" get_param "docker.env.MEMORY")
if [ -z "$MEMORY_EXISTS" ]; then
  MEMORY=$(read_tty "Memory (e.g. 2G / 4G): ")
  if [ -n "$MEMORY" ]; then
    PARAM_KEY="docker.env.MEMORY" PARAM_VALUE="$MEMORY" set_param "docker.env.MEMORY" "$MEMORY"
  fi
fi

EXPECTED_PLAYERS=$(PARAM_KEY="deploy.expected_players" get_param "deploy.expected_players")
if [ -z "$EXPECTED_PLAYERS" ]; then
  EXPECTED_PLAYERS=$(read_tty "Expected players (optional): ")
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
python3 - <<'PY'
import json
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
        print(f\"{key}\\t{'' if hint is None else hint}\\t{dtype}\\t{'' if min_val is None else min_val}\\t{'' if max_val is None else max_val}\")
PY > /tmp/param_keys.txt

while IFS=$'\t' read -r key default_hint dtype min_val max_val; do
  existing=$(PARAM_KEY="$key" get_param "$key")
  if [ -n "$existing" ]; then
    continue
  fi
  if [ -n "$default_hint" ]; then
    prompt="Set ${key} [default: ${default_hint}]: "
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

CLAIMS_STRING=$(python3 - <<'PY'
import json
import os
from deploy.claims_codec.encode import encode_claims
with open(os.environ["PARAMS_JSON"], "r", encoding="utf-8") as handle:
    params = json.load(handle)
print(encode_claims(params))
PY
)

echo ""
echo "[INFO] Running plan..."
PLAN_OUTPUT=$(python3 -m deploy.cli plan \
  --version "$VERSION" \
  --profile "$PROFILE" \
  --import-string "$CLAIMS_STRING")
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
  --version "$VERSION" \
  --profile "$PROFILE" \
  --import-string "$CLAIMS_STRING" \
  --dry-run

echo ""
echo "Reusable claims string:"
echo "$CLAIMS_STRING"
echo ""
echo "[INFO] Execution plan complete (dry-run only)."
exit 0
