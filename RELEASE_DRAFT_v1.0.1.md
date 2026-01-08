# MC Panel v1.0.1 / v1.0.1 补丁说明

This patch release fixes deploy flow issues reported after v1.0.0.
本补丁版本修复 v1.0.0 后反馈的部署流程问题。

AI Usage Notice / AI 使用说明
This project was developed by a single person (freshman year). Due to limited time and technical resources, AI assistance was heavily used throughout the implementation.
本项目由单人（大一）完成，受限于时间与技术资源，开发过程中大量使用 AI 辅助。

Fixes / 修复
- Language selection added at the start of install flow.
- Minecraft version input is now a menu + validated custom entry.
- Map plugin choice validates download URL; failed option no longer proceeds.
- Blocked plan now allows interactive adjustments before exit.
- Player-scope block rule relaxed to warn with recommendations (e.g., allow-flight).

- 安装流程开始处加入语言选择。
- 版本输入改为菜单 + 校验的自定义输入。
- 地图插件下载链接可达性校验，失败不继续。
- plan 被 block 后允许交互式调整再继续。
- 玩家范围参数从 block 调整为 warn + 推荐（如 allow-flight）。

Quick start / 快速开始
```
curl -fsSL https://raw.githubusercontent.com/zalataraglados-prog/mc-panel-sanitized/v1.0.1/install.sh | sudo bash
```
