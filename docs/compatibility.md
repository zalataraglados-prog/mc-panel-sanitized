# Compatibility Matrix (Modpack / Stack) / 兼容矩阵（整合包 / Stack）

This project supports optional modpack compatibility checks in the planner.
These checks are opt-in: they only run when you provide modpack parameters.

本项目在 Planner 中支持可选的整合包兼容性检查。
这些检查为可选，仅在提供 modpack 参数时生效。

## Parameters / 参数

Set one of the following in claims params (via `--set` or import-string):

- `modpack.loader` (preferred)
- `modpack.type`
- `modpack.stack`
- `modpack.name` or `modpack.slug` (optional; for lookup)

在 claims params 中设置如下字段（`--set` 或导入字符串）：

- `modpack.loader`（推荐）
- `modpack.type`
- `modpack.stack`
- `modpack.name` 或 `modpack.slug`（可选，用于检索）

Example / 示例：

```
--set modpack.loader=fabric
--set stack.type=fabric
```

## Matrix (v1) / 矩阵（v1）

| Modpack loader | Compatible stack.type |
|---------------|-----------------------|
| vanilla       | vanilla, paper        |
| paper         | paper                 |
| fabric        | fabric                |
| forge         | forge                 |
| neoforge      | neoforge              |

If `modpack.loader` is provided without `stack.type`, the planner blocks.
If `modpack.name` is provided without a loader, the planner will attempt to map
the name to a loader using the Modrinth top-400 index (by downloads).

若提供 `modpack.loader` 但缺少 `stack.type`，Planner 会阻拦。
若仅提供 `modpack.name`，Planner 会尝试根据 Modrinth Top-400（按下载量）推断 loader。

## Notes / 说明

- This matrix does not install mods or packs.
- It only validates compatibility; execution is unchanged.

- 该矩阵不负责安装模组或整合包。
- 仅做兼容性校验，执行层不变。
