# Changelog / 更新日志

## [Unreleased] / 未发布

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
