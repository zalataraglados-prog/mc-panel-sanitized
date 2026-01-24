# MC Panel v1.0.2 / v1.0.2 发布草案

This release focuses on panel stability and operator workflows for small servers.
本次发布聚焦面板稳定性与服主/管理流程。

## Highlights / 亮点

- Inventory UI now supports full Chinese item names via official `zh_cn.json`.
  - 背包物品中文名全量覆盖（官方 `zh_cn.json`）。
- Owner panel with per-instance `owners.json` and owner-only controls.
  - 服主栏支持实例级 `owners.json`，仅服主可管理。
- Map preview embeds BlueMap (port 8100) with a direct open button.
  - 地图预览内嵌 8100 端口 BlueMap，并提供“打开详细地图”按钮。
- Inventory editing supports offline playerdata and online RCON replace.
  - 支持离线 NBT 读取与在线 RCON 写入背包。

## Upgrade / 升级

```
git pull
cd frontend
npm install
npm run build
sudo systemctl restart mc-panel
```

## Install / 安装

```
curl -fsSL https://raw.githubusercontent.com/zalataraglados-prog/mc-panel-sanitized/v1.0.2/install.sh | sudo bash
```

## Notes / 说明

- If you hit an error, copy the error output together with the README and share it with any AI you can reach.
- 如遇报错，将报错连同 README 复制给你能接触到的 AI，通常能快速定位问题。
