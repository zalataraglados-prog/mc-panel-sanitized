# Mod / Plugin Compatibility Notes

This project tracks a decision engine that refuses unreasonable stack+mod/plugin combinations. Summary:

1. **Vanilla stack** only accepts base server parameters. Any `mods.*` or `plugins.*` parameter is blocked.
2. **Fabric/Forge/NeoForge stacks** allow mod-related parameters but block traditional Bukkit plugins (`plugins.*`).
3. **Paper stack** allows plugins but blocks mods (Forge/Fabric/NeoForge style).
4. **Compatibility warnings** appear as `stack_param_conflict` in the planner review and include taxonomy metadata (`category=compatibility`, `scope=world`). The web review can translate these hints into English/Chinese for display.

If you deploy a modded server, ensure the `stack.type` matches your runtime:

| stack.type | supports mods | supports plugins |
|------------|---------------|------------------|
| vanilla    | ❌            | ❌               |
| paper      | ❌            | ✅               |
| fabric     | ✅            | ❌               |
| forge      | ✅            | ❌               |
| neoforge   | ✅            | ❌               |

The planner will always report a block if you mix incompatible parameters, producing a translated warning/hint so the UI can explain the issue.
