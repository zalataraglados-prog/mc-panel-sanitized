# MC Panel (demon1.3)

## Release Notice / 閸欐垵绔锋竟鐗堟

- Important: The first two releases (v1.0.0 / v1.0.1) contain critical defects and must not be used in production.
- 闁插秷顩﹂敍姘娑撱倓閲滃锝呯础閻楀牞绱檝1.0.0 / v1.0.1閿涘鐡ㄩ崷銊ゅ紬闁插秶宸遍梽鍑ょ礉鐠囧嘲瀣侀悽銊ょ艾閻㈢喍楠囬悳顖氼暔閵?
- If you hit an error, copy the error output together with this README and share it with any AI you can reach; it resolves most issues quickly.
- 婵″倿浜ｉ幎銉╂晩閿涘苯鐨㈤幎銉╂晩鏉╃偛鎮撻張顑跨矙缂佸秴顦查崚鍓佺舶娴ｇ姾鍏橀幒銉ㄐ曢崚鎵畱 AI閿涘苯褰叉禒銉ㄐ掗崘宕囩卜婢堆囧劥閸掑棝妫舵０妯糕偓?

## Release / 瑜版挸澧犻崣鎴濈

- Current release: `v1.0.2`
- Tag: `https://github.com/zalataraglados-prog/mc-panel-sanitized/releases/tag/v1.0.2`
- Notes: see `RELEASE_DRAFT_v1.0.2.md`

- 瑜版挸澧犻悧鍫熸拱閿涙瓪v1.0.2`
- 閺嶅洨顒烽敍姝歨ttps://github.com/zalataraglados-prog/mc-panel-sanitized/releases/tag/v1.0.2`
- 鐠囧瓨妲戦敍姘愁潌 `RELEASE_DRAFT_v1.0.2.md`

This project is a configuration decision engine for Minecraft deployments with an optional runtime panel.
閺堫剟銆嶉惄顔芥Ц娑撯偓娑?Minecraft 闁劎璁查崜宥囨畱闁板秶鐤嗙憗浣稿枀瀵洘鎼搁敍宀冪箥鐞涘本婀￠棃銏℃緲娑撳搫褰查柅澶岀矋娴犺翰鈧?

## Quick start (plan + dry-run) / 韫囶偊鈧喎绱戞慨瀣剁礄娴?plan + dry-run閿?

```
curl -fsSL https://raw.githubusercontent.com/zalataraglados-prog/mc-panel-sanitized/demon1.3/install.sh | sudo bash
```

After the first install, you can use the short CLI (Linux only):
瀹夎瀹屾垚鍚庡彲浣跨敤绠€鍐?CLI锛堜粎 Linux锛夛細

```
mcic
```

MCIC command dictionary (lean):
MCIC 命令字典（精简）：

- `mcic plan` 生成评审（不执行）
- `mcic apply` 执行部署
- `mcic ls` 列出实例
- `mcic use <ins>` 设定默认实例
- `mcic status | logs | ports | players` 常用查看
- `mcic op|deop|tp|kick|ban|unban <player>` 管理命令
- `mcic inv|inv-export|inv-import <player>` 背包查看/导入导出
- `mcic map | map-reload` 地图相关
- `mcic diag` 诊断
- `mcic otp` 获取向导口令
- `mcic tui` 旧路径（终端交互）

Instance resolution order / 实例解析优先级
1) `--instance-dir` / `--instance`
2) 环境变量 `MCIC_INSTANCE` / `MC_PANEL_INSTANCE`
3) `~/.mcic_default`（`mcic use` 写入）
4) 自动推断唯一实例（仅在只有一个实例时）

3) `~/.mcic_default`閿涘潉mcic use` 閸愭瑥鍙嗛敍?4) 閼奉亜濮╅幒銊︽焽閸烆垯绔寸€圭偘绶ラ敍鍫滅矌閸︺劌褰ч張澶夌娑擃亜鐤勬笟瀣閿?## Network resilience / 缂冩垹绮堕崣顖炴浆閹?

The installer retries external HTTP fetches with backoff to survive flaky networks.
鐎瑰顥婇懘姘拱鐎电懓顦婚柈銊嚞濮瑰倽鍤滈崝銊╁櫢鐠囨洖鑻熼幐鍥ㄦ殶闁偓闁尅绱濋崙蹇撶毌閸ョ姷缍夌紒婊勫皾閸斻劌顕遍懛瀵告畱婢惰精瑙﹂妴?

Optional environment variables:
閸欘垶鈧骞嗘晶鍐ㄥ綁闁插骏绱?

- `MC_PANEL_HTTP_RETRIES` (default 3) / 闁插秷鐦▎鈩冩殶
- `MC_PANEL_HTTP_BACKOFF_SECONDS` (default 2) / 閸掓繂顫愰柅鈧柆璺潡閺?

### Docker mirror & proxy pull / Docker 闂€婊冨剼閸旂娀鈧喍绗屾禒锝囨倞閹峰褰?

If Docker Hub is unreachable, the installer can prompt for a mirror or a proxy prefix:
瑜?Docker Hub 娑撳秴褰叉潏鐐閿涘苯鐣ㄧ憗鍛板壖閺堫兛绱伴幓鎰仛娴ｇ娀鍘ょ純顕€鏆呴崓蹇撳闁喐鍨ㄦ禒锝囨倞閸撳秶绱戦敍?

- Mirror prompt (writes `/etc/docker/daemon.json`, restarts Docker)
- Proxy pull prompt (pre-pulls via proxy and tags locally)

Environment variables (skip prompts):
閻滎垰顣ㄩ崣姗€鍣洪敍鍫ｇ儲鏉╁洣姘︽禍鎺炵礆閿?

- `MC_PANEL_DOCKER_MIRRORS` (comma-separated, e.g. `https://a.mirror,https://b.mirror`)
- `MC_PANEL_DOCKER_MIRROR` (legacy single mirror, still supported)
- `MC_PANEL_DOCKER_PROXY_PREFIX` (e.g. `m.daocloud.io/docker.io`)

If `itzg/minecraft-server:latest` already exists locally, the installer skips the proxy prompt.
閼汇儲婀伴崷鏉垮嚒鐎涙ê婀?`itzg/minecraft-server:latest`閿涘苯鐣ㄧ憗鍛板壖閺堫兛绱扮捄瀹犵箖娴狅絿鎮婇幓鎰仛閵?

Example (manual proxy pull):
缁€杞扮伐閿涘牊澧滈崝銊ゅ敩閻炲棙濯洪崣鏍电礆閿?

```
sudo docker pull m.daocloud.io/docker.io/itzg/minecraft-server:latest
sudo docker tag m.daocloud.io/docker.io/itzg/minecraft-server:latest itzg/minecraft-server:latest
```

### Multi-mirror fallback / 婢舵岸鏆呴崓蹇旂爱閸忔粌绨?

Docker will try registry mirrors in order; configure multiple mirrors to improve resilience.
Docker 娴兼碍瀵滄い鍝勭碍鐏忔繆鐦梹婊冨剼濠ф劧绱遍柊宥囩枂婢舵矮閲滈梹婊冨剼濠ф劘鍏橀幓鎰磳閹存劕濮涢悳鍥モ偓?

The mirror prompt also accepts multiple comma-separated URLs.
闂€婊冨剼閹绘劗銇氶崥灞剧壉閺€顖涘瘮婢舵矮閲滈柅妤€褰块崚鍡涙閻ㄥ嫬婀撮崸鈧妴?

```
sudo tee /etc/docker/daemon.json >/dev/null <<'EOF'
{"registry-mirrors":["https://mirror-a.example.com","https://mirror-b.example.com"]}
EOF
sudo systemctl restart docker
```

## Optional Web Panel / 閸欘垶鈧?Web 闂堛垺婢?

The panel is optional. It can be installed during deploy or added later without affecting the server.
闂堛垺婢橀弰顖氬讲闁銆嶉敍灞藉讲閸︺劑鍎寸純鍙夋鐎瑰顥婇敍灞肩瘍閸欘垶鍎寸純鎻掓倵鐞涖儴顥婇敍灞肩瑬娑撳秴濂栭崫宥嗘箛閸斺€虫珤閺堫兛缍嬮妴?

### Panel prerequisites / 闂堛垺婢樻笟婵婄

- Python packages: `fastapi`, `uvicorn`
- Frontend build output: `frontend/dist` (build with Node.js + npm)

- Python 娓氭繆绂嗛敍姝歠astapi`, `uvicorn`
- 閸撳秶顏弸鍕紦娴溠呭⒖閿涙瓪frontend/dist`閿涘牅濞囬悽?Node.js + npm 閺嬪嫬缂撻敍?

The installer auto-builds the frontend when panel is enabled and npm is available.
閼汇儱鎯庨悽銊╂桨閺夊じ绗?npm 閸欘垳鏁ら敍灞界暔鐟佸懓鍓奸張顑跨窗閼奉亜濮╅弸鍕紦閸撳秶顏妴?

Command input rule:
Panel commands do NOT need a leading `/`. In-game chat commands still use `/`.

閹稿洣鎶ゆ潏鎾冲弳鐟欏嫬鍨敍?
闂堛垺婢橀幐鍥︽姢娑撳秹娓剁憰浣稿缂?`/`閿涘本鐖堕幋蹇氫喊婢垛晙鑵戞禒宥夋付 `/`閵?

### Install panel during deploy / 闁劎璁查弮璺虹暔鐟佸懘娼伴弶?

When running `install.sh`, choose:
`Install Web Panel? [y/N]`

閹笛嗩攽 `install.sh` 閺冨爼鈧瀚ㄩ敍?
`Install Web Panel? [y/N]`

### Panel maintenance mode (existing instance) / 闂堛垺婢樼紒瀛樺Б濡€崇础閿涘牆鍑￠張澶婄杽娓氬绱?

`install.sh` offers a maintenance menu before deploy:

- Install panel for an existing instance
- Uninstall panel from an existing instance

`install.sh` 閸︺劑鍎寸純鎻掑閹绘劒绶电紒瀛樺Б閼挎粌宕熼敍?

- 娑撳搫鍑￠張澶婄杽娓氬鐣ㄧ憗鍛存桨閺?
- 閸楁瓕娴囧鍙夋箒鐎圭偘绶ラ棃銏℃緲

The panel is a single service (`mc-panel.service`) that can manage multiple instances.
闂堛垺婢樻稉鍝勫礋娑撯偓閺堝秴濮熼敍鍧刴c-panel.service`閿涘绱濋崣顖滎吀閻炲棗顦挎稉顏勭杽娓氬鈧?

### Add panel to an existing instance / 缂佹瑥鍑￠張澶婄杽娓氬藟鐟佸懘娼伴弶?

```
sudo python3 -m deploy.cli panel install --instance-dir /opt/mc-instances/<instance-name>
```

Options / 閸欘垶鈧寮弫甯窗

- `--panel-port 15000` to override port / 娣囶喗鏁肩粩顖氬經
- `--no-start` to avoid starting the service immediately / 娑撳秶鐝涢崡鍐叉儙閸斻劍婀囬崝?
- `--no-build` to skip frontend build / 鐠哄疇绻冮崜宥囶伂閺嬪嫬缂?
- `--panel-root /opt/mc-panel-sanitized` to point to the repo root / 閹稿洤鐣炬禒鎾崇氨閺嶅湱娲拌ぐ?

### Uninstall panel from an instance / 娴犲骸鐤勬笟瀣祻鏉炰粙娼伴弶?

```
sudo python3 -m deploy.cli panel uninstall --instance-dir /opt/mc-instances/<instance-name>
```

## Map plugins / 閸︽澘娴橀幓鎺嶆

During deploy, you can optionally enable Dynmap or BlueMap. The deployer can configure:
闁劎璁查弮璺哄讲闁?Dynmap 閹?BlueMap閿涘矂鍎寸純鎻掓珤閸欘垶鍘ょ純顕嗙窗

- plugin port (`map.plugin_port`) / 閹绘帊娆㈢粩顖氬經
- render interval (`map.render_interval`) / 濞撳弶鐓嬮梻鎾
- optional world file copy (`map.file`, `map.target`, `map.overwrite`) / 閸欘垶鈧绗橀悾灞炬瀮娴犺泛顕遍崗?

### BlueMap (Paper required) / BlueMap閿涘牓娓剁憰?Paper閿?

If `map.plugin=bluemap` is selected, the deployer forces `docker.env.TYPE=PAPER` to ensure plugin loading.
BlueMap requires accepting resource download in `core.conf` and will not render until it has generated tiles.
The deployer sets `accept-download: true` by default.

婵″倹鐏夐柅澶嬪 `map.plugin=bluemap`閿涘矂鍎寸純鎻掓珤娴兼艾宸遍崚?`docker.env.TYPE=PAPER` 娴犮儳鈥樻穱婵囧絻娴犺泛褰查崝鐘烘祰閵?
BlueMap 闂団偓鐟曚礁婀?`core.conf` 娑擃厼鍘戠拋姝岀カ濠ф劒绗呮潪鏂ょ礉閻㈢喐鍨氶悺锔惧閸氬孩澧犳导姘閺屾挶鈧?
闁劎璁查崳銊╃帛鐠併倛顔曠純?`accept-download: true`閵?

The panel shows a live preview by embedding the external BlueMap viewer (port 8100),
and provides a button to open the detailed map in a new window.
闂堛垺婢橀崘鍛サ 8100 缁旑垰褰涢惃?BlueMap 妞ょ敻娼版担婊€璐熸０鍕潔閿涘苯鑻熼幓鎰返閹稿鎸抽幍鎾崇磻鐠囷妇绮忛崷鏉挎禈閵?

If BlueMap has no tiles yet, run:
`bluemap render world` (panel/RCON) or `/bluemap render world` (in-game).

閼?BlueMap 鐏忔碍婀悽鐔稿灇閻★妇澧栭敍宀冾嚞閹笛嗩攽閿?
`bluemap render world`閿涘牓娼伴弶?RCON閿涘鍨?`/bluemap render world`閿涘牊鐖堕幋蹇撳敶閿涘鈧?

## Inventory plugins / 閼冲苯瀵橀幓鎺嶆

During deploy, you can optionally install an inventory plugin for richer inventory editing.
Supported choices: InvSee++ or OpenInv. Defaults point to the `vanilla_catalog` repository, but you can override the URL.

闁劎璁查弮璺哄讲闁鐣ㄧ憗鍛板剹閸栧懏褰冩禒鍓佹暏娴滃孩娲挎稉鏉跨槣閻ㄥ嫯鍎楅崠鍛椽鏉堟垯鈧?
閺€顖涘瘮閿涙nvSee++ 閹?OpenInv閵嗗倿绮拋銈勭瑓鏉炶姤绨幐鍥ф倻 `vanilla_catalog` 娴犳挸绨遍敍灞肩瘍閸欘垵顩惄?URL閵?

### Offline inventory editing / 缁傝崵鍤庨懗灞藉瘶缂傛牞绶?

If OpenInv is installed and the player has joined at least once (so `usercache.json` exists),
the panel can read/write the offline inventory directly from `world/playerdata/*.dat`.
Online players are still handled via RCON.

閼汇儱鐣ㄧ憗?OpenInv 娑撴梻甯虹€规儼鍤︾亸鎴ｇ箻閸忋儴绻冩稉鈧▎鈽呯礄鐎涙ê婀?`usercache.json`閿涘绱?
闂堛垺婢橀崣顖滄纯閹恒儴顕伴崣?閸愭瑥鍙?`world/playerdata/*.dat`閵?
閸︺劎鍤庨悳鈺侇啀娴犲秹鈧俺绻?RCON 婢跺嫮鎮婇妴?

## Modpack compatibility / 閺佹潙鎮庨崠鍛悑鐎?

If you provide `modpack.loader` (or `modpack.type`/`modpack.stack`) in claims params,
the planner validates it against the stack compatibility matrix. See `docs/compatibility.md`.
You can also provide `modpack.name`/`modpack.slug` to infer loader from the Modrinth top-400 index.

婵″倹鐏夐崷銊ュ棘閺侀鑵戦幓鎰返 `modpack.loader`閿涘牊鍨?`modpack.type`/`modpack.stack`閿涘绱?
Planner 娴兼碍瀵滈崗鐓庮啇閻晠妯€閺嶏繝鐛欓敍宀冾嚊鐟?`docs/compatibility.md`閵?
娑旂喎褰查幓鎰返 `modpack.name`/`modpack.slug` 娴?Modrinth Top-400 閹恒劍鏌?loader閵?

## Plugin download logging / 閹绘帊娆㈡稉瀣祰閺冦儱绻?

Download failures are appended to `logs/plugin_download.log`. If log push is enabled,
the deployer will attempt to push updates to the `logs` branch in the repo.

閹绘帊娆㈡稉瀣祰婢惰精瑙︽导姘愁唶瑜版洖鍩?`logs/plugin_download.log`閵?
閼汇儱鎯庨悽銊︽）韫囨甯归柅渚婄礉闁劎璁查崳銊ょ窗鐏忔繆鐦亸鍡樻纯閺傜増甯归柅浣稿煂娴犳挸绨?`logs` 閸掑棙鏁妴?

## CLI event logging (optional) / CLI 娴滃娆㈤弮銉ョ箶閿涘牆褰查柅澶涚礆

Set `MC_PANEL_CLI_LOG=1` to append review + execution plan events to `logs/cli_events.jsonl`.
You can override the log directory with `MC_PANEL_LOG_DIR`.

鐠佸墽鐤?`MC_PANEL_CLI_LOG=1` 閸欘垰鐨?review 娑撳孩澧界悰宀冾吀閸掓帟顔囪ぐ鏇炲煂 `logs/cli_events.jsonl`閵?
閸欘垳鏁?`MC_PANEL_LOG_DIR` 鐟曞棛娲婇弮銉ョ箶閻╊喖缍嶉妴?

## Rules data source / 鐟欏嫬鍨弫鐗堝祦閺夈儲绨?

Catalog/Taxonomy are stored in the external rules repository.
Catalog/Taxonomy 鐎涙ɑ鏂侀崷銊ヮ樆闁劏顫夐崚娆庣波鎼存挶鈧?

- https://raw.githubusercontent.com/zalataraglados-prog/vanilla_catalog/main/catalog/vanilla_1.21.11.json
- https://raw.githubusercontent.com/zalataraglados-prog/vanilla_catalog/main/taxonomy/vanilla_1.21.11.json

## Memory format / 閸愬懎鐡ㄩ弽鐓庣础

`docker.env.MEMORY` accepts integers or decimals (e.g. `2G`, `2.5G`).
Decimals are normalized to MB before starting the server to avoid JVM errors.

`docker.env.MEMORY` 閺€顖涘瘮閺佸瓨鏆熼幋鏍х毈閺佸府绱欐俊?`2G`, `2.5G`閿涘鈧?
鐏忓繑鏆熸导姘冲殰閸斻劏娴嗛幑顫礋 MB 閸愬秴鎯庨崝銊︽箛閸斺€虫珤閿涘矂浼╅崗?JVM 閸欏倹鏆熼幎銉╂晩閵?


## Localization / ????

- Web panel UI (frontend)
- Wizard UI (port 15001)
- CLI prompts & docs (mcic)

- Web ????????
- ???????15001 ???
- CLI ??????mcic?