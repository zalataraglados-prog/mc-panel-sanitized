# MC Panel (demon1.3)

## Release Notice / 闁告瑦鍨电粩閿嬬珶閻楀牊顫?

- Important: The first two releases (v1.0.0 / v1.0.1) contain critical defects and must not be used in production.
- 闂佹彃绉烽々锕傛晬濮橆剙顤呭☉鎾卞€撻柌婊冾潰閿濆懐纭€闁绘鐗炵槐妾?.0.0 / v1.0.1闁挎稑顦悺銊╁捶閵娿倕绱梺鎻掔Ф瀹搁亶姊介崙銈囩閻犲洤鍢茬€ｄ線鎮介妸銈囪壘闁汇垻鍠嶆鍥偝椤栨凹鏆旈柕?
- If you hit an error, copy the error output together with this README and share it with any AI you can reach; it resolves most issues quickly.
- 濠碘€冲€挎禍锝夊箮閵夆晜鏅╅柨娑樿嫰閻ㄣ垽骞庨妷鈺傛櫓閺夆晝鍋涢幃鎾诲嫉椤戣法鐭欑紓浣哥Т椤︽煡宕氶崜浣鸿埗濞达絿濮鹃崗姗€骞掗妷銊愭洟宕氶幍顔界暠 AI闁挎稑鑻ぐ鍙夌閵夈剱鎺楀礃瀹曞洨鍗滃鍫嗗洤鍔ラ柛鎺戞濡埖锛愬Ο绯曞亾?

## Release / 鐟滅増鎸告晶鐘诲矗閹存繄顏?

- Current release: `v1.0.2`
- Tag: `https://github.com/zalataraglados-prog/mc-panel-sanitized/releases/tag/v1.0.2`
- Notes: see `RELEASE_DRAFT_v1.0.2.md`

- 鐟滅増鎸告晶鐘绘偋閸喐鎷遍柨娑欑摢v1.0.2`
- 闁哄秴娲ㄩ鐑芥晬濮濇ttps://github.com/zalataraglados-prog/mc-panel-sanitized/releases/tag/v1.0.2`
- 閻犲洤鐡ㄥΣ鎴︽晬濮樻剚娼?`RELEASE_DRAFT_v1.0.2.md`

This project is a configuration decision engine for Minecraft deployments with an optional runtime panel.
闁哄牜鍓熼妴宥夋儎椤旇姤笑濞戞挴鍋撳☉?Minecraft 闂侇喓鍔庣拋鏌ュ礈瀹ュ洦鐣遍梺鏉跨Ф閻ゅ棛鎲楁担绋挎瀫鐎殿喗娲橀幖鎼佹晬瀹€鍐閻炴稑鏈﹢锟犳閵忊剝绶插☉鎾虫惈瑜版煡鏌呮径宀€鐭嬪ù鐘虹堪閳?

## Quick start (plan + dry-run) / 闊浂鍋婇埀顒傚枎缁辨垶鎱ㄧ€ｅ墎绀勫ù?plan + dry-run闁?

```
curl -fsSL https://raw.githubusercontent.com/zalataraglados-prog/mc-panel-sanitized/demon1.3/install.sh | sudo bash
```

After the first install, you can use the short CLI (Linux only):
鐎瑰顥婄€瑰本鍨氶崥搴″讲娴ｈ法鏁ょ粻鈧崘?CLI閿涘牅绮?Linux閿涘绱?

```
mcic
```

Instance resolution order / 瀹炰緥瑙ｆ瀽浼樺厛绾?
1) `--instance-dir` / `--instance`
2) 鐜鍙橀噺 `MCIC_INSTANCE` / `MC_PANEL_INSTANCE`
3) `~/.mcic_default`锛坄mcic use` 鍐欏叆锛?
4) 鑷姩鎺ㄦ柇鍞竴瀹炰緥锛堜粎鍦ㄥ彧鏈変竴涓疄渚嬫椂锛?

3) `~/.mcic_default`闁挎稑娼塵cic use` 闁告劖鐟ラ崣鍡涙晬?4) 闁煎浜滄慨鈺呭箳閵婏附鐒介柛鐑嗗灟缁斿鈧湱鍋樼欢銉╂晬閸粎鐭岄柛锔哄妼瑜把囧嫉婢跺顏卞☉鎿冧簻閻ゅ嫭绗熺€ｎ偅顦ч柨?## Network resilience / 缂傚啯鍨圭划鍫曞矗椤栫偞娴嗛柟?

The installer retries external HTTP fetches with backoff to survive flaky networks.
閻庣懓顦抽ˉ濠囨嚇濮橆厽鎷遍悗鐢垫嚀椤﹀鏌堥妸顭戝殲婵懓鍊介崵婊堝礉閵娾晛娅㈤悹鍥ㄦ礀閼荤喖骞愰崶銊︽闂侇偀鍋撻梺顒€灏呯槐婵嬪礄韫囨挾姣岄柛銉уХ缂嶅绱掑鍕毦闁告柣鍔岄閬嶆嚊鐎靛憡鐣卞鎯扮簿鐟欙箓濡?

Optional environment variables:
闁告瑯鍨堕埀顒€顦遍獮鍡樻櫠閸愩劌缍侀梺鎻掗獜缁?

- `MC_PANEL_HTTP_RETRIES` (default 3) / 闂佹彃绉烽惁顖氣枎閳╁啯娈?
- `MC_PANEL_HTTP_BACKOFF_SECONDS` (default 2) / 闁告帗绻傞～鎰版焻閳ь剟鏌嗙捄顭戞健闁?

### Docker mirror & proxy pull / Docker 闂傗偓濠婂啫鍓奸柛鏃傚█閳ь剛鍠嶇粭灞剧閿濆洦鍊為柟宄邦槸瑜?

If Docker Hub is unreachable, the installer can prompt for a mirror or a proxy prefix:
鐟?Docker Hub 濞戞挸绉磋ぐ鍙夋綇閻愵剚顦ч柨娑樿嫰閻ｃ劎鎲楅崨鏉垮闁哄牜鍏涚槐浼村箵閹邦喓浠涘ù锝囧█閸樸倗绱旈鈧弳鍛村磽韫囨挸顫ｉ梺顐ゅ枑閸ㄣ劍绂掗敐鍥ㄥ€為柛鎾崇Ф缁辨垿鏁?

- Mirror prompt (writes `/etc/docker/daemon.json`, restarts Docker)
- Proxy pull prompt (pre-pulls via proxy and tags locally)

Environment variables (skip prompts):
闁绘粠鍨伴。銊╁矗濮椻偓閸ｆ椽鏁嶉崼锝囧劜閺夆晛娲ｅ锔界閹虹偟绀嗛柨?

- `MC_PANEL_DOCKER_MIRRORS` (comma-separated, e.g. `https://a.mirror,https://b.mirror`)
- `MC_PANEL_DOCKER_MIRROR` (legacy single mirror, still supported)
- `MC_PANEL_DOCKER_PROXY_PREFIX` (e.g. `m.daocloud.io/docker.io`)

If `itzg/minecraft-server:latest` already exists locally, the installer skips the proxy prompt.
闁兼眹鍎插﹢浼村捶閺夊灝鍤掗悗娑櫭﹢?`itzg/minecraft-server:latest`闁挎稑鑻悾銊ф啑閸涙澘澹栭柡鍫厸缁辨壆鎹勭€圭姷绠栧ù鐙呯悼閹﹪骞撻幇顔轰粵闁?

Example (manual proxy pull):
缂佲偓鏉炴壆浼愰柨娑樼墛婢ф粓宕濋妸銈呮暕闁荤偛妫欐刊娲矗閺嶇數绀嗛柨?

```
sudo docker pull m.daocloud.io/docker.io/itzg/minecraft-server:latest
sudo docker tag m.daocloud.io/docker.io/itzg/minecraft-server:latest itzg/minecraft-server:latest
```

### Multi-mirror fallback / 濠㈣埖宀搁弳鍛村磽韫囨梻鐖遍柛蹇旂矊缁?

Docker will try registry mirrors in order; configure multiple mirrors to improve resilience.
Docker 濞村吋纰嶇€垫粍銇勯崫鍕閻忓繑绻嗛惁顖炴⒐濠婂啫鍓兼繝褎鍔х槐閬嶆煀瀹ュ洨鏋傚鑸电煯闁叉粓姊瑰鍐ㄥ壖婵犙勫姌閸忔﹢骞撻幇顒€纾抽柟瀛樺姇婵盯鎮抽崶銉㈠亾?

The mirror prompt also accepts multiple comma-separated URLs.
闂傗偓濠婂啫鍓奸柟缁樺姉閵囨岸宕ョ仦鍓у闁衡偓椤栨稑鐦鑸电煯闁叉粓鏌呭Δ鈧ぐ鍧楀礆閸℃稒顓鹃柣銊ュ濠€鎾锤閳ь剟濡?

```
sudo tee /etc/docker/daemon.json >/dev/null <<'EOF'
{"registry-mirrors":["https://mirror-a.example.com","https://mirror-b.example.com"]}
EOF
sudo systemctl restart docker
```

## Optional Web Panel / 闁告瑯鍨堕埀?Web 闂傚牄鍨哄?

The panel is optional. It can be installed during deploy or added later without affecting the server.
闂傚牄鍨哄姗€寮伴姘闂侇偄顦甸妴宥夋晬鐏炶棄璁查柛锔哄姂閸庡绱旈崣澶嬵槯閻庣懓顦抽ˉ濠囨晬鐏炶偐鐦嶉柛娆樺灦閸庡绱旈幓鎺撳€甸悶娑栧劥椤ュ﹪鏁嶇仦鑲╃懍濞戞挸绉存總鏍传瀹ュ棙绠涢柛鏂衡偓铏彜闁哄牜鍏涚紞瀣Υ?

### Panel prerequisites / 闂傚牄鍨哄妯荤瑹濠靛﹦顩?

- Python packages: `fastapi`, `uvicorn`
- Frontend build output: `frontend/dist` (build with Node.js + npm)

- Python 濞撴碍绻嗙粋鍡涙晬濮濇瓲astapi`, `uvicorn`
- 闁告挸绉堕顒勫几閸曨偆绱﹀ù婧犲懎鈷栭柨娑欑摢frontend/dist`闁挎稑鐗呮繛鍥偨?Node.js + npm 闁哄瀚紓鎾绘晬?

The installer auto-builds the frontend when panel is enabled and npm is available.
闁兼眹鍎遍幆搴ㄦ偨閵娾晜妗ㄩ柡澶娿仒缁?npm 闁告瑯鍨抽弫銈夋晬鐏炵晫鏆旈悷浣告嚀閸撳ジ寮甸璺ㄧ獥闁煎浜滄慨鈺呭几閸曨偆绱﹂柛鎾崇Ф椤忣剟濡?

Command input rule:
Panel commands do NOT need a leading `/`. In-game chat commands still use `/`.

闁圭娲ｉ幎銈嗘綇閹惧啿寮抽悷娆忓閸垶鏁?
闂傚牄鍨哄姗€骞愰崶锔藉Б濞戞挸绉瑰〒鍓佹啺娴ｇ顤呯紓?`/`闁挎稑鏈悥鍫曞箣韫囨矮鍠婂鍨涙櫃閼垫垶绂掑澶嬩粯 `/`闁?

### Install panel during deploy / 闂侇喓鍔庣拋鏌ュ籍鐠鸿櫣鏆旈悷浣告嚇濞间即寮?

When running `install.sh`, choose:
`Install Web Panel? [y/N]`

闁圭瑳鍡╂斀 `install.sh` 闁哄啫鐖奸埀顒€顦扮€氥劑鏁?
`Install Web Panel? [y/N]`

### Panel maintenance mode (existing instance) / 闂傚牄鍨哄妯肩磼鐎涙ê袘婵☆垪鈧磭纭€闁挎稑鐗嗛崙锟犲嫉婢跺﹦鏉藉〒姘儜缁?

`install.sh` offers a maintenance menu before deploy:

- Install panel for an existing instance
- Uninstall panel from an existing instance

`install.sh` 闁革负鍔戦崕瀵哥磾閹绘帒顤呴柟缁樺姃缁剁數绱掔€涙ê袘闁兼寧绮屽畷鐔兼晬?

- 濞戞挸鎼崙锟犲嫉婢跺﹦鏉藉〒姘儏閻ｃ劎鎲楅崨瀛樻〃闁?
- 闁告鐡曞ù鍥ь啅閸欏绠掗悗鍦仒缁躲儵妫冮姀鈩冪凡

The panel is a single service (`mc-panel.service`) that can manage multiple instances.
闂傚牄鍨哄妯荤▔閸濆嫬绀嬪☉鎾亾闁哄牆绉存慨鐔兼晬閸у埓c-panel.service`闁挎稑顧€缁辨繈宕ｉ婊庡悁闁荤偛妫楅ˇ鎸庣▔椤忓嫮鏉藉〒姘儍閳?

### Add panel to an existing instance / 缂備焦鐟ラ崙锟犲嫉婢跺﹦鏉藉〒姘儓钘熼悷浣告嚇濞间即寮?

```
sudo python3 -m deploy.cli panel install --instance-dir /opt/mc-instances/<instance-name>
```

Options / 闁告瑯鍨堕埀顒€顦顒勫极鐢喚绐?

- `--panel-port 15000` to override port / 濞ｅ浂鍠楅弫鑲╃博椤栨艾缍?
- `--no-start` to avoid starting the service immediately / 濞戞挸绉堕悵娑㈠础閸愬弶鍎欓柛鏂诲妽濠€鍥礉?
- `--no-build` to skip frontend build / 閻犲搫鐤囩换鍐礈瀹ュ浂浼傞柡瀣缂?
- `--panel-root /opt/mc-panel-sanitized` to point to the repo root / 闁圭娲ら悾鐐閹惧磭姘ㄩ柡宥呮贡濞叉媽銇?

### Uninstall panel from an instance / 濞寸姴楠搁悿鍕瑹鐎ｎ亜绁婚弶鐐扮矙濞间即寮?

```
sudo python3 -m deploy.cli panel uninstall --instance-dir /opt/mc-instances/<instance-name>
```

## Map plugins / 闁革附婢樺ù姗€骞撻幒宥嗩偨

During deploy, you can optionally enable Dynmap or BlueMap. The deployer can configure:
闂侇喓鍔庣拋鏌ュ籍鐠哄搫璁查梺?Dynmap 闁?BlueMap闁挎稑鐭傞崕瀵哥磾閹绘帗鐝ら柛娆樺灦閸樸倗绱旈鍡欑獥

- plugin port (`map.plugin_port`) / 闁圭粯甯婂▎銏㈢博椤栨艾缍?
- render interval (`map.render_interval`) / 婵炴挸寮堕悡瀣⒒閹绢喗顓?
- optional world file copy (`map.file`, `map.target`, `map.overwrite`) / 闁告瑯鍨堕埀顒€顦粭姗€鎮剧仦鐐€ù鐘烘硾椤曢亶宕?

### BlueMap (Paper required) / BlueMap闁挎稑鐗撳〒鍓佹啺?Paper闁?

If `map.plugin=bluemap` is selected, the deployer forces `docker.env.TYPE=PAPER` to ensure plugin loading.
BlueMap requires accepting resource download in `core.conf` and will not render until it has generated tiles.
The deployer sets `accept-download: true` by default.

濠碘€冲€归悘澶愭焻婢跺顏?`map.plugin=bluemap`闁挎稑鐭傞崕瀵哥磾閹绘帗鐝ゅù鍏艰壘瀹搁亶宕?`docker.env.TYPE=PAPER` 濞寸姰鍎抽垾妯荤┍濠靛洤绲诲ù鐘烘硾瑜版煡宕濋悩鐑樼グ闁?
BlueMap 闂傚洠鍋撻悷鏇氱濠€?`core.conf` 濞戞搩鍘奸崢鎴犳媼濮濆瞼銈繝褎鍔掔粭鍛姜閺傘倗绀夐柣銏㈠枑閸ㄦ岸鎮洪敂鎯ь暬闁告艾瀛╂晶鐘冲濮橆叀顩柡灞炬尪閳?
闂侇喓鍔庣拋鏌ュ闯閵娾晝甯涢悹浣靛€涢鏇犵磾?`accept-download: true`闁?

The panel shows a live preview by embedding the external BlueMap viewer (port 8100),
and provides a button to open the detailed map in a new window.
闂傚牄鍨哄姗€宕橀崨顓犮偟 8100 缂佹棏鍨拌ぐ娑㈡儍?BlueMap 濡炪倗鏁诲鐗堟媴濠娾偓鐠愮喐锛愰崟顕呮綌闁挎稑鑻懟鐔煎箵閹邦亞杩旈柟绋款樀閹告娊骞嶉幘宕囩；閻犲浄濡囩划蹇涘捶閺夋寧绂堥柕?

If BlueMap has no tiles yet, run:
`bluemap render world` (panel/RCON) or `/bluemap render world` (in-game).

闁?BlueMap 閻忓繑纰嶅﹢顓㈡偨閻旂鐏囬柣鈽呭婢ф牠鏁嶅畝鍐惧殲闁圭瑳鍡╂斀闁?
`bluemap render world`闁挎稑鐗撳浼村级?RCON闁挎稑顦伴崹?`/bluemap render world`闁挎稑鐗婇悥鍫曞箣韫囨挸鏁堕柨娑橆槶閳?

## Inventory plugins / 闁煎啿鑻€垫﹢骞撻幒宥嗩偨

During deploy, you can optionally install an inventory plugin for richer inventory editing.
Supported choices: InvSee++ or OpenInv. Defaults point to the `vanilla_catalog` repository, but you can override the URL.

闂侇喓鍔庣拋鏌ュ籍鐠哄搫璁查梺顐㈩槸閻ｃ劎鎲楅崨鏉垮壒闁告牕鎳忚ぐ鍐╃閸撲焦鏆忓ù婊冨濞叉寧绋夐弶璺ㄦВ闁汇劌瀚崕妤呭礌閸涱垳妞介弶鍫熷灟閳?
闁衡偓椤栨稑鐦柨娑欘儣nvSee++ 闁?OpenInv闁靛棗鍊跨划顖滄媼閵堝嫮鐟撻弶鐐跺Г缁噣骞愰崶褎鍊?`vanilla_catalog` 濞寸姵鎸哥花閬嶆晬鐏炶偐鐦嶉柛娆樺灥椤╊偊鎯?URL闁?

### Offline inventory editing / 缂佸倽宕甸崵搴ㄦ嚄鐏炶棄鐦剁紓鍌涚墳缁?

If OpenInv is installed and the player has joined at least once (so `usercache.json` exists),
the panel can read/write the offline inventory directly from `world/playerdata/*.dat`.
Online players are still handled via RCON.

闁兼眹鍎遍悾銊ф啑?OpenInv 濞戞挻姊荤敮铏光偓瑙勫劶閸わ妇浜搁幋锝囩闁稿繈鍎寸换鍐╃▔閳ь剙鈻庨埥鍛閻庢稒锚濠€?`usercache.json`闁挎稑顧€缁?
闂傚牄鍨哄姗€宕ｉ婊勭函闁规亽鍎撮浼村矗?闁告劖鐟ラ崣?`world/playerdata/*.dat`闁?
闁革负鍔庨崵搴ㄦ偝閳轰緡鍟€濞寸姴绉归埀顒佷亢缁?RCON 濠㈣泛瀚幃濠囧Υ?

## Modpack compatibility / 闁轰焦娼欓幃搴ㄥ礌閸涱厼鎮戦悗?

If you provide `modpack.loader` (or `modpack.type`/`modpack.stack`) in claims params,
the planner validates it against the stack compatibility matrix. See `docs/compatibility.md`.
You can also provide `modpack.name`/`modpack.slug` to infer loader from the Modrinth top-400 index.

濠碘€冲€归悘澶愬捶閵娿儱妫橀柡渚€顣﹂懙鎴﹀箵閹邦亞杩?`modpack.loader`闁挎稑鐗婇崹?`modpack.type`/`modpack.stack`闁挎稑顧€缁?
Planner 濞村吋纰嶇€垫粓宕楅悡搴晣闁活厸鏅犲Ο鈧柡宥忕節閻涙瑩鏁嶅畝鍐惧殜閻?`docs/compatibility.md`闁?
濞戞梻鍠庤ぐ鏌ュ箵閹邦亞杩?`modpack.name`/`modpack.slug` 濞?Modrinth Top-400 闁规亽鍔嶉弻?loader闁?

## Plugin download logging / 闁圭粯甯婂▎銏＄▔鐎ｎ厽绁伴柡鍐﹀劚缁?

Download failures are appended to `logs/plugin_download.log`. If log push is enabled,
the deployer will attempt to push updates to the `logs` branch in the repo.

闁圭粯甯婂▎銏＄▔鐎ｎ厽绁板鎯扮簿鐟欙附瀵煎鎰佸敹鐟滅増娲栭崺?`logs/plugin_download.log`闁?
闁兼眹鍎遍幆搴ㄦ偨閵婏附锛夐煫鍥殕鐢綊鏌呮笟濠勭闂侇喓鍔庣拋鏌ュ闯閵娿倗绐楅悘蹇旂箚閻︻垳浜搁崱妯荤函闁哄倻澧楃敮褰掓焻娴ｇ鐓傚ù鐘虫尭缁?`logs` 闁告帒妫欓弫顕€濡?

## CLI event logging (optional) / CLI 濞存粌顑勫▎銏ゅ籍閵夈儳绠堕柨娑樼墕瑜版煡鏌呮径娑氱

Set `MC_PANEL_CLI_LOG=1` to append review + execution plan events to `logs/cli_events.jsonl`.
You can override the log directory with `MC_PANEL_LOG_DIR`.

閻犱礁澧介悿?`MC_PANEL_CLI_LOG=1` 闁告瑯鍨伴惃?review 濞戞挸瀛╂晶鐣屾偘瀹€鍐惧悁闁告帗甯熼鍥亹閺囩偛鐓?`logs/cli_events.jsonl`闁?
闁告瑯鍨抽弫?`MC_PANEL_LOG_DIR` 閻熸洖妫涘ú濠囧籍閵夈儳绠堕柣鈺婂枛缂嶅秹濡?

## Rules data source / 閻熸瑥瀚崹顖炲极閻楀牆绁﹂柡澶堝劜缁?

Catalog/Taxonomy are stored in the external rules repository.
Catalog/Taxonomy 閻庢稒蓱閺備線宕烽妸銉▎闂侇喓鍔忛～澶愬礆濞嗗海娉㈤幖瀛樻尪閳?

- https://raw.githubusercontent.com/zalataraglados-prog/vanilla_catalog/main/catalog/vanilla_1.21.11.json
- https://raw.githubusercontent.com/zalataraglados-prog/vanilla_catalog/main/taxonomy/vanilla_1.21.11.json

## Memory format / 闁告劕鎳庨悺銊╁冀閻撳海纭€

`docker.env.MEMORY` accepts integers or decimals (e.g. `2G`, `2.5G`).
Decimals are normalized to MB before starting the server to avoid JVM errors.

`docker.env.MEMORY` 闁衡偓椤栨稑鐦柡浣哥摠閺嗙喖骞嬮弽褏姣堥柡浣稿簻缁辨瑦淇?`2G`, `2.5G`闁挎稑顦埀?
閻忓繐绻戦弳鐔稿濮樺啿娈伴柛鏂诲姀濞村棝骞戦～顓＄ MB 闁告劕绉撮幆搴ㄥ礉閵婏附绠涢柛鏂衡偓铏彜闁挎稑鐭傛导鈺呭礂?JVM 闁告瑥鍊归弳鐔煎箮閵夆晜鏅╅柕?


## Localization / ????

- Web panel UI (frontend)
- Wizard UI (port 15001)
- CLI prompts & docs (mcic)

- Web ????????
- ???????15001 ???
- CLI ??????mcic?