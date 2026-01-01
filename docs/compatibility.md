# Compatibility Matrix (Modpack / Stack)

This project supports optional modpack compatibility checks in the planner.
These checks are opt-in: they only run when you provide modpack parameters.

## Parameters

Set one of the following in claims params (via `--set` or import-string):

- `modpack.loader` (preferred)
- `modpack.type`
- `modpack.stack`
- `modpack.name` or `modpack.slug` (optional; for lookup)

Example:

```
--set modpack.loader=fabric
--set stack.type=fabric
```

## Matrix (v1)

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

## Notes

- This matrix does not install mods or packs.
- It only validates compatibility; execution is unchanged.
