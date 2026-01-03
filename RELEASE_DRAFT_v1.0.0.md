# MC Panel v1.0.0

This release marks the first stable, publishable version of the Minecraft Configuration Decision Engine with an optional runtime panel.

AI Usage Notice
This project was developed by a single person (freshman year). Due to limited time and technical resources, AI assistance was heavily used throughout the implementation.

Highlights
- Rules-driven planning: catalog + taxonomy + planner -> allow/warn/block/recommend.
- Loader: pulls rules from the remote rules repository.
- Execution Plan (dry-run): deterministic, auditable plan output.
- Claims string: params-only import/export.
- Optional runtime panel: FastAPI backend + React frontend.

Key Features
- Review output: warnings, blocks, recommendations.
- CLI: plan/apply (dry-run default), instances listing, panel install/uninstall.
- Panel: metrics, logs, command/RCON, players, map tiles, rules editor, inventory (via optional plugin).
- Map plugins: Dynmap/BlueMap optional support, config reload via RCON.
- Plugin download logging with optional git push to logs branch.

Notes
- Panel is optional and can be installed later.
- This release does not auto-apply recommendations or execute system changes by default.

If you want to verify locally:
```
curl -fsSL https://raw.githubusercontent.com/zalataraglados-prog/mc-panel-sanitized/demon1.1/install.sh | sudo bash
```
