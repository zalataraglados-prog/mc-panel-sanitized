# MC Panel (demon1.3)

## Release Notice / 鍙戝竷澹版槑

- Important: The first two releases (v1.0.0 / v1.0.1) contain critical defects and must not be used in production.
- 閲嶈锛氬墠涓や釜姝ｅ紡鐗堬紙v1.0.0 / v1.0.1锛夊瓨鍦ㄤ弗閲嶇己闄凤紝璇峰嬁鐢ㄤ簬鐢熶骇鐜銆?
- If you hit an error, copy the error output together with this README and share it with any AI you can reach; it resolves most issues quickly.
- 濡傞亣鎶ラ敊锛屽皢鎶ラ敊杩炲悓鏈粙缁嶅鍒剁粰浣犺兘鎺ヨЕ鍒扮殑 AI锛屽彲浠ヨВ鍐崇粷澶ч儴鍒嗛棶棰樸€?

## Release / 褰撳墠鍙戝竷

- Current release: `v1.0.2`
- Tag: `https://github.com/zalataraglados-prog/mc-panel-sanitized/releases/tag/v1.0.2`
- Notes: see `RELEASE_DRAFT_v1.0.2.md`

- 褰撳墠鐗堟湰锛歚v1.0.2`
- 鏍囩锛歚https://github.com/zalataraglados-prog/mc-panel-sanitized/releases/tag/v1.0.2`
- 璇存槑锛氳 `RELEASE_DRAFT_v1.0.2.md`

This project is a configuration decision engine for Minecraft deployments with an optional runtime panel.
鏈」鐩槸涓€涓?Minecraft 閮ㄧ讲鍓嶇殑閰嶇疆瑁佸喅寮曟搸锛岃繍琛屾湡闈㈡澘涓哄彲閫夌粍浠躲€?

## Quick start (plan + dry-run) / 蹇€熷紑濮嬶紙浠?plan + dry-run锛?

```
curl -fsSL https://raw.githubusercontent.com/zalataraglados-prog/mc-panel-sanitized/demon1.3/install.sh | sudo bash
```

After the first install, you can use the short CLI (Linux only):
安装完成后可使用简写 CLI（仅 Linux）：

```
mcic
```

MCIC command dictionary (full):
MCIC 命令字典（完整版）：

Common instance flags (most commands support these):
通用实例参数（多数命令可用）：
- `--instance-dir <path>` 实例目录
- `--instance <name>` 实例名
- `--base-dir <path>` 实例根目录（默认 /opt/mc-instances）

Core workflow:
核心流程：
- `mcic plan` 生成评审（不执行）
  - `--version <ver>` Minecraft 版本（默认 1.21.11）
  - `--profile <beginner|normal|advanced>` 配置档位
  - `--set key=value` 追加参数（可重复）
  - `--import-string <claims>` 从配置串导入
  - `--import-file <path>` 从文件导入
  - `--import-format <auto|full|compact|min>` 导入格式
  - `--rules-base-url <url>` 规则仓库 base URL
  - `--rules-ref <tag|commit|branch>` 规则仓库 ref
- `mcic apply` 执行部署
  - 支持与 `plan` 相同的全部参数
  - `--dry-run` 仅生成执行计划（默认）
  - `--apply` 真正执行部署
  - `--no-review` 跳过评审输出（已评审时用）
  - `--confirm-warn` 允许 warn 等级继续

Instance list / select:
实例管理：
- `mcic ls` 列出实例
- `mcic use <ins>` 设置默认实例（`<ins>` 为实例名或路径）
- `mcic instances` 列出实例（完整路径）

Panel management:
面板管理：
- `mcic panel install` 安装面板
  - `--instance-dir <path>` 指定实例
  - `--base-dir <path>` 实例根目录
  - `--panel-port <port>` 指定面板端口
  - `--panel-root <path>` 指定面板仓库路径
  - `--no-start` 不启动服务
  - `--no-build` 跳过前端构建
- `mcic panel uninstall` 卸载面板
  - `--instance-dir <path>` 指定实例
  - `--base-dir <path>` 实例根目录

Runtime controls:
运行控制：
- `mcic up | down | restart`
- `mcic status | logs | ports | players`

RCON helpers:
常用管理：
- `mcic op|deop <player> [level]` 赋权/撤权（level 在高版本忽略）
- `mcic tp <player> <x> <y> <z>` 传送
- `mcic kick <player> [reason...]`
- `mcic ban <player> [reason...]`
- `mcic unban <player>`
- `mcic map | map-reload`
- `mcic diag`

Inventory:
背包相关：
- `mcic inv <player>` 查看背包
- `mcic inv-export <player> --out <file>` 导出背包 JSON
- `mcic inv-import <player> <file>` 导入背包 JSON

Wizard / legacy:
向导 / 兼容：
- `mcic otp` 显示向导一次性口令（向导启用时）
  - `--log <path>` 指定日志
  - `--token <path>` 指定 token 文件
- `mcic tui` 进入传统 TUI（面板失效时）
  - `tui [plan|apply] [--version/--profile/--import-* ...]`

Instance resolution order / 实例解析优先级
1) `--instance-dir` / `--instance`
2) 环境变量 `MCIC_INSTANCE` / `MC_PANEL_INSTANCE`
3) `~/.mcic_default`（`mcic use` 写入）
4) 自动推断唯一实例（仅在只有一个实例时）

3) `~/.mcic_default`锛坄mcic use` 鍐欏叆锛?4) 鑷姩鎺ㄦ柇鍞竴瀹炰緥锛堜粎鍦ㄥ彧鏈変竴涓疄渚嬫椂锛?## Network resilience / 缃戠粶鍙潬鎬?

The installer retries external HTTP fetches with backoff to survive flaky networks.
瀹夎鑴氭湰瀵瑰閮ㄨ姹傝嚜鍔ㄩ噸璇曞苟鎸囨暟閫€閬匡紝鍑忓皯鍥犵綉缁滄尝鍔ㄥ鑷寸殑澶辫触銆?

Optional environment variables:
鍙€夌幆澧冨彉閲忥細

- `MC_PANEL_HTTP_RETRIES` (default 3) / 閲嶈瘯娆℃暟
- `MC_PANEL_HTTP_BACKOFF_SECONDS` (default 2) / 鍒濆閫€閬跨鏁?

### Docker mirror & proxy pull / Docker 闀滃儚鍔犻€熶笌浠ｇ悊鎷夊彇

If Docker Hub is unreachable, the installer can prompt for a mirror or a proxy prefix:
褰?Docker Hub 涓嶅彲杈炬椂锛屽畨瑁呰剼鏈細鎻愮ず浣犻厤缃暅鍍忓姞閫熸垨浠ｇ悊鍓嶇紑锛?

- Mirror prompt (writes `/etc/docker/daemon.json`, restarts Docker)
- Proxy pull prompt (pre-pulls via proxy and tags locally)

Environment variables (skip prompts):
鐜鍙橀噺锛堣烦杩囦氦浜掞級锛?

- `MC_PANEL_DOCKER_MIRRORS` (comma-separated, e.g. `https://a.mirror,https://b.mirror`)
- `MC_PANEL_DOCKER_MIRROR` (legacy single mirror, still supported)
- `MC_PANEL_DOCKER_PROXY_PREFIX` (e.g. `m.daocloud.io/docker.io`)

If `itzg/minecraft-server:latest` already exists locally, the installer skips the proxy prompt.
鑻ユ湰鍦板凡瀛樺湪 `itzg/minecraft-server:latest`锛屽畨瑁呰剼鏈細璺宠繃浠ｇ悊鎻愮ず銆?

Example (manual proxy pull):
绀轰緥锛堟墜鍔ㄤ唬鐞嗘媺鍙栵級锛?

```
sudo docker pull m.daocloud.io/docker.io/itzg/minecraft-server:latest
sudo docker tag m.daocloud.io/docker.io/itzg/minecraft-server:latest itzg/minecraft-server:latest
```

### Multi-mirror fallback / 澶氶暅鍍忔簮鍏滃簳

Docker will try registry mirrors in order; configure multiple mirrors to improve resilience.
Docker 浼氭寜椤哄簭灏濊瘯闀滃儚婧愶紱閰嶇疆澶氫釜闀滃儚婧愯兘鎻愬崌鎴愬姛鐜囥€?

The mirror prompt also accepts multiple comma-separated URLs.
闀滃儚鎻愮ず鍚屾牱鏀寔澶氫釜閫楀彿鍒嗛殧鐨勫湴鍧€銆?

```
sudo tee /etc/docker/daemon.json >/dev/null <<'EOF'
{"registry-mirrors":["https://mirror-a.example.com","https://mirror-b.example.com"]}
EOF
sudo systemctl restart docker
```

## Optional Web Panel / 鍙€?Web 闈㈡澘

The panel is optional. It can be installed during deploy or added later without affecting the server.
闈㈡澘鏄彲閫夐」锛屽彲鍦ㄩ儴缃叉椂瀹夎锛屼篃鍙儴缃插悗琛ヨ锛屼笖涓嶅奖鍝嶆湇鍔″櫒鏈綋銆?

### Panel prerequisites / 闈㈡澘渚濊禆

- Python packages: `fastapi`, `uvicorn`
- Frontend build output: `frontend/dist` (build with Node.js + npm)

- Python 渚濊禆锛歚fastapi`, `uvicorn`
- 鍓嶇鏋勫缓浜х墿锛歚frontend/dist`锛堜娇鐢?Node.js + npm 鏋勫缓锛?

The installer auto-builds the frontend when panel is enabled and npm is available.
鑻ュ惎鐢ㄩ潰鏉夸笖 npm 鍙敤锛屽畨瑁呰剼鏈細鑷姩鏋勫缓鍓嶇銆?

Command input rule:
Panel commands do NOT need a leading `/`. In-game chat commands still use `/`.

鎸囦护杈撳叆瑙勫垯锛?
闈㈡澘鎸囦护涓嶉渶瑕佸墠缃?`/`锛屾父鎴忚亰澶╀腑浠嶉渶 `/`銆?

### Install panel during deploy / 閮ㄧ讲鏃跺畨瑁呴潰鏉?

When running `install.sh`, choose:
`Install Web Panel? [y/N]`

鎵ц `install.sh` 鏃堕€夋嫨锛?
`Install Web Panel? [y/N]`

### Panel maintenance mode (existing instance) / 闈㈡澘缁存姢妯″紡锛堝凡鏈夊疄渚嬶級

`install.sh` offers a maintenance menu before deploy:

- Install panel for an existing instance
- Uninstall panel from an existing instance

`install.sh` 鍦ㄩ儴缃插墠鎻愪緵缁存姢鑿滃崟锛?

- 涓哄凡鏈夊疄渚嬪畨瑁呴潰鏉?
- 鍗歌浇宸叉湁瀹炰緥闈㈡澘

The panel is a single service (`mc-panel.service`) that can manage multiple instances.
闈㈡澘涓哄崟涓€鏈嶅姟锛坄mc-panel.service`锛夛紝鍙鐞嗗涓疄渚嬨€?

### Add panel to an existing instance / 缁欏凡鏈夊疄渚嬭ˉ瑁呴潰鏉?

```
sudo python3 -m deploy.cli panel install --instance-dir /opt/mc-instances/<instance-name>
```

Options / 鍙€夊弬鏁帮細

- `--panel-port 15000` to override port / 淇敼绔彛
- `--no-start` to avoid starting the service immediately / 涓嶇珛鍗冲惎鍔ㄦ湇鍔?
- `--no-build` to skip frontend build / 璺宠繃鍓嶇鏋勫缓
- `--panel-root /opt/mc-panel-sanitized` to point to the repo root / 鎸囧畾浠撳簱鏍圭洰褰?

### Uninstall panel from an instance / 浠庡疄渚嬪嵏杞介潰鏉?

```
sudo python3 -m deploy.cli panel uninstall --instance-dir /opt/mc-instances/<instance-name>
```

## Map plugins / 鍦板浘鎻掍欢

During deploy, you can optionally enable Dynmap or BlueMap. The deployer can configure:
閮ㄧ讲鏃跺彲閫?Dynmap 鎴?BlueMap锛岄儴缃插櫒鍙厤缃細

- plugin port (`map.plugin_port`) / 鎻掍欢绔彛
- render interval (`map.render_interval`) / 娓叉煋闂撮殧
- optional world file copy (`map.file`, `map.target`, `map.overwrite`) / 鍙€変笘鐣屾枃浠跺鍏?

### BlueMap (Paper required) / BlueMap锛堥渶瑕?Paper锛?

If `map.plugin=bluemap` is selected, the deployer forces `docker.env.TYPE=PAPER` to ensure plugin loading.
BlueMap requires accepting resource download in `core.conf` and will not render until it has generated tiles.
The deployer sets `accept-download: true` by default.

濡傛灉閫夋嫨 `map.plugin=bluemap`锛岄儴缃插櫒浼氬己鍒?`docker.env.TYPE=PAPER` 浠ョ‘淇濇彃浠跺彲鍔犺浇銆?
BlueMap 闇€瑕佸湪 `core.conf` 涓厑璁歌祫婧愪笅杞斤紝鐢熸垚鐡︾墖鍚庢墠浼氭覆鏌撱€?
閮ㄧ讲鍣ㄩ粯璁よ缃?`accept-download: true`銆?

The panel shows a live preview by embedding the external BlueMap viewer (port 8100),
and provides a button to open the detailed map in a new window.
闈㈡澘鍐呭祵 8100 绔彛鐨?BlueMap 椤甸潰浣滀负棰勮锛屽苟鎻愪緵鎸夐挳鎵撳紑璇︾粏鍦板浘銆?

If BlueMap has no tiles yet, run:
`bluemap render world` (panel/RCON) or `/bluemap render world` (in-game).

鑻?BlueMap 灏氭湭鐢熸垚鐡︾墖锛岃鎵ц锛?
`bluemap render world`锛堥潰鏉?RCON锛夋垨 `/bluemap render world`锛堟父鎴忓唴锛夈€?

## Inventory plugins / 鑳屽寘鎻掍欢

During deploy, you can optionally install an inventory plugin for richer inventory editing.
Supported choices: InvSee++ or OpenInv. Defaults point to the `vanilla_catalog` repository, but you can override the URL.

閮ㄧ讲鏃跺彲閫夊畨瑁呰儗鍖呮彃浠剁敤浜庢洿涓板瘜鐨勮儗鍖呯紪杈戙€?
鏀寔锛欼nvSee++ 鎴?OpenInv銆傞粯璁や笅杞芥簮鎸囧悜 `vanilla_catalog` 浠撳簱锛屼篃鍙鐩?URL銆?

### Offline inventory editing / 绂荤嚎鑳屽寘缂栬緫

If OpenInv is installed and the player has joined at least once (so `usercache.json` exists),
the panel can read/write the offline inventory directly from `world/playerdata/*.dat`.
Online players are still handled via RCON.

鑻ュ畨瑁?OpenInv 涓旂帺瀹惰嚦灏戣繘鍏ヨ繃涓€娆★紙瀛樺湪 `usercache.json`锛夛紝
闈㈡澘鍙洿鎺ヨ鍙?鍐欏叆 `world/playerdata/*.dat`銆?
鍦ㄧ嚎鐜╁浠嶉€氳繃 RCON 澶勭悊銆?

## Modpack compatibility / 鏁村悎鍖呭吋瀹?

If you provide `modpack.loader` (or `modpack.type`/`modpack.stack`) in claims params,
the planner validates it against the stack compatibility matrix. See `docs/compatibility.md`.
You can also provide `modpack.name`/`modpack.slug` to infer loader from the Modrinth top-400 index.

濡傛灉鍦ㄥ弬鏁颁腑鎻愪緵 `modpack.loader`锛堟垨 `modpack.type`/`modpack.stack`锛夛紝
Planner 浼氭寜鍏煎鐭╅樀鏍￠獙锛岃瑙?`docs/compatibility.md`銆?
涔熷彲鎻愪緵 `modpack.name`/`modpack.slug` 浠?Modrinth Top-400 鎺ㄦ柇 loader銆?

## Plugin download logging / 鎻掍欢涓嬭浇鏃ュ織

Download failures are appended to `logs/plugin_download.log`. If log push is enabled,
the deployer will attempt to push updates to the `logs` branch in the repo.

鎻掍欢涓嬭浇澶辫触浼氳褰曞埌 `logs/plugin_download.log`銆?
鑻ュ惎鐢ㄦ棩蹇楁帹閫侊紝閮ㄧ讲鍣ㄤ細灏濊瘯灏嗘洿鏂版帹閫佸埌浠撳簱 `logs` 鍒嗘敮銆?

## CLI event logging (optional) / CLI 浜嬩欢鏃ュ織锛堝彲閫夛級

Set `MC_PANEL_CLI_LOG=1` to append review + execution plan events to `logs/cli_events.jsonl`.
You can override the log directory with `MC_PANEL_LOG_DIR`.

璁剧疆 `MC_PANEL_CLI_LOG=1` 鍙皢 review 涓庢墽琛岃鍒掕褰曞埌 `logs/cli_events.jsonl`銆?
鍙敤 `MC_PANEL_LOG_DIR` 瑕嗙洊鏃ュ織鐩綍銆?

## Rules data source / 瑙勫垯鏁版嵁鏉ユ簮

Catalog/Taxonomy are stored in the external rules repository.
Catalog/Taxonomy 瀛樻斁鍦ㄥ閮ㄨ鍒欎粨搴撱€?

- https://raw.githubusercontent.com/zalataraglados-prog/vanilla_catalog/main/catalog/vanilla_1.21.11.json
- https://raw.githubusercontent.com/zalataraglados-prog/vanilla_catalog/main/taxonomy/vanilla_1.21.11.json

## Memory format / 鍐呭瓨鏍煎紡

`docker.env.MEMORY` accepts integers or decimals (e.g. `2G`, `2.5G`).
Decimals are normalized to MB before starting the server to avoid JVM errors.

`docker.env.MEMORY` 鏀寔鏁存暟鎴栧皬鏁帮紙濡?`2G`, `2.5G`锛夈€?
灏忔暟浼氳嚜鍔ㄨ浆鎹负 MB 鍐嶅惎鍔ㄦ湇鍔″櫒锛岄伩鍏?JVM 鍙傛暟鎶ラ敊銆?


## Localization / ????

- Web panel UI (frontend)
- Wizard UI (port 15001)
- CLI prompts & docs (mcic)

- Web ????????
- ???????15001 ???
- CLI ??????mcic?
