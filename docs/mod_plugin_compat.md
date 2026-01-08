# Mod / Plugin Compatibility Notes / 模组与插件兼容说明

This project tracks a decision engine that refuses unreasonable stack+mod/plugin combinations.
Summary:

本项目的裁决引擎会拒绝不合理的 stack 与 mod/plugin 组合。
摘要如下：

1. **Vanilla stack** only accepts base server parameters. Any `mods.*` or `plugins.*` parameter is blocked.
2. **Fabric/Forge/NeoForge stacks** allow mod-related parameters but block traditional Bukkit plugins (`plugins.*`).
3. **Paper stack** allows plugins but blocks mods (Forge/Fabric/NeoForge style).
4. **Compatibility warnings** appear as `stack_param_conflict` in the planner review and include taxonomy metadata (`category=compatibility`, `scope=world`). The web review can translate these hints into English/Chinese for display.

1. **Vanilla stack** 仅接受基础服务器参数，任何 `mods.*` / `plugins.*` 都会被阻拦。
2. **Fabric/Forge/NeoForge** 允许模组参数，但阻止 Bukkit 插件（`plugins.*`）。
3. **Paper stack** 支持插件，但阻止 Forge/Fabric/NeoForge 模组参数。
4. **兼容性警告** 以 `stack_param_conflict` 呈现，并带 taxonomy 元数据（`category=compatibility`, `scope=world`），Web 可中英双语展示。

If you deploy a modded server, ensure the `stack.type` matches your runtime:
部署模组服时，请确保 `stack.type` 与运行时一致：

| stack.type | supports mods | supports plugins |
|------------|---------------|------------------|
| vanilla    | no            | no               |
| paper      | no            | yes              |
| fabric     | yes           | no               |
| forge      | yes           | no               |
| neoforge   | yes           | no               |

The planner will always report a block if you mix incompatible parameters, producing a translated warning/hint so the UI can explain the issue.
若混用不兼容参数，Planner 会产生 block，并生成可翻译的提示用于 UI 解释。
