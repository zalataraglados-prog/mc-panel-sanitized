# MC Panel v1.0.0 Release Notes

This release marks the first stable, publishable version of the Minecraft Configuration Decision Engine with optional runtime panel.

Highlights
- Rules-driven planning: catalog + taxonomy + planner -> allow/warn/block/recommend.
- Loader: pulls rules from remote repository, injects into planner.
- Execution Plan (dry-run): deterministic, auditable plan output.
- Claims string: import/export of params-only payloads.
- Optional runtime panel: FastAPI backend + React frontend.

Key Features
- Review output: warnings, blocks, recommendations.
- CLI: plan/apply (dry-run default), instances listing, panel install/uninstall.
- Panel: metrics, logs, command/RCON, player list, map tiles, rules editor, inventory (via optional plugin).
- Map plugins: Dynmap/BlueMap optional support, config reload via RCON.
- Plugin download logging with optional git push to logs branch.

Notes
- Panel is optional and can be installed later.
- This release does not auto-apply recommendations or execute system changes by default.

Changes since demon1.1 baseline
- API aggregation and throttling (summary endpoint, cache).
- Frontend polling throttled to reduce load.
- Optional CLI event logging.
- Documentation updates for summary API and CLI logs.
