# Changelog / 更新日志

## [Unreleased] / 未发布

## [2026-01-30]
### Added / 新增
- Web wizard (port 15001) with plan/apply UI, OTP protection, apply progress bar, and modal feedback.
  - 新增 15001 端口部署向导：OTP 保护、Apply 进度条与弹窗反馈。
- Wizard OTP signing with nonce (optional), plus `mcic otp` helper and legacy `mcic tui` alias.
  - 向导 OTP 支持带随机数签名；新增 `mcic otp`；`mcic legacy` 作为 `tui` 入口。

### Changed / 调整
- Wizard i18n toggle and full Chinese text coverage in the wizard UI.
  - 向导页支持中英文切换并补齐中文文案。
- Wizard apply now uses `--apply` and provides explicit completion/failure feedback.
  - Apply 操作传递 `--apply` 并返回明确完成/失败提示。
- Limit optional map/inventory plugins to supported choices only.
  - 地图/背包插件限制为可用项。
- Default Minecraft version bumped to 1.21.11.
  - 默认版本更新为 1.21.11。

### Fixed / 修复
- Wizard/CLI stability: lock + workdir guard + interrupt cleanup; stale wizard PID cleanup before restart.
  - CLI/向导：运行锁、工作目录恢复、Ctrl+C 清理；服务重启前清理旧 PID。
- Wizard responses now include `Content-Length` and close connections reliably.
  - 向导响应增加 `Content-Length` 并主动关闭连接，避免挂起。
- Node/npm install conflicts handled via Corepack in install flow.
  - 安装流程对 Node/npm 冲突进行 Corepack 兼容处理。


## [2026-01-24]
### Added / 新增
- Full Chinese item name map in inventory UI using the official `zh_cn.json`.
  - 背包界面接入官方 `zh_cn.json`，物品中文名全量覆盖。
- Owner panel with per-instance `owners.json`, owner-only controls, and logout button.
  - 新增服主栏（实例级 `owners.json`）、服主专属操作与退出登录按钮。

### Changed / 调整
- Map view simplified to embed the external BlueMap page (port 8100) with a dedicated open button.
  - 地图改为内嵌 8100 端口 BlueMap 预览，并提供“打开详细地图”按钮。
- Inventory editing UI switched to a slot grid with hotbar at the bottom.
  - 背包编辑界面改为格子布局，快捷栏在底部。

### Fixed / 修复
- Inventory read/write supports offline playerdata and online editing via RCON item replace.
  - 支持离线 NBT 读取与在线 RCON 写入背包。
- Memory format normalization for decimal values to avoid JVM `-Xmx` errors.
  - 内存小数格式自动标准化，避免 JVM 启动失败。

## [2026-01-06]
### Added / 新增
- RCON health check endpoint and UI status badge (`/api/rcon/health`, status tag in dashboard).
  - 新增 RCON 健康检查接口与面板状态标识（`/api/rcon/health`）。
- Claims export API (`/api/claims/export`) and UI button to export the full defaults + overrides as a claims string.
  - 新增配置导出接口与面板导出按钮（全量默认 + 覆盖）。
- Gamerule export via RCON during claims export (fallback to defaults when RCON fails).
  - 导出时通过 RCON 读取 gamerule（失败则回退默认值）。
- Recommendation sampling tool for planner validation (`deploy/tools/recommendation_sampling.py`).
  - 新增 Planner 推荐采样验证脚本。
- Player OP level selector (1-4) in the player card UI.
  - 玩家卡片新增 OP 等级选择（1-4）。

### Changed / 调整
- RCON connection now resolves host port from instance `config.json` or `docker-compose.yml` before falling back to `server.properties`.
  - RCON 连接优先从 `config.json` / `docker-compose.yml` 读取端口，失败才回退 `server.properties`。
- Planner scope warnings now trigger only when a parameter is explicitly changed (avoids default-noise warnings).
  - 仅当参数被显式修改时才触发 scope 警告，避免默认值噪音。
- Capacity guard: warn when `memory <= required` (keeps block thresholds intact).
  - 容量护栏：`memory <= required` 时警告（block 门槛不变）。
- install.sh now pre-fills params with catalog defaults and merges imported claims; prompt loop uses defaults as visible values.
  - install.sh 预填 catalog 默认值并合并导入配置；交互显示默认值。

### Fixed / 修复
- Claims import no longer loses defaults when used in combination with manual overrides.
  - 导入字符串与手动覆盖组合时不会丢失默认值。
- Web UI now exposes clear RCON error feedback.
  - 面板显示更清晰的 RCON 错误反馈。
