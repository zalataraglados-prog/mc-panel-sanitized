# MC Panel Deploy (PoC)

This branch only keeps the deploy tooling: a Python-based, opinionated bootstrapper that provisions a Minecraft server instance with Docker and systemd using the templates in `deploy/templates/`.

## What it does
- Checks prerequisites (root, Docker, Compose).
- Asks for an instance name, creates structure under `/opt/mc-instances/<name>/`.
- Auto-generates `config.json`, `docker-compose.yml`, and a `mc-<name>.service` unit.
- Brings the stack up and enables/starts the systemd service.

## Prerequisites
- Linux host with Docker and docker-compose available in PATH.
- Run as root (the script enforces this).
- The web panel build is expected at `../web-panel` relative to `deploy/` (see `WEB_PANEL_PATH` in `deploy/setup.py`).

## Quick start
```bash
git checkout deploy-only
python3 deploy/setup.py
```

The script will prompt for an instance name, generate files, run `docker-compose up`, and configure `systemd` for `mc-<name>.service`.

## Layout
- `deploy/core/` runtime logic: env checks, naming, instance creation, compose/systemd generators, deployer.
- `deploy/templates/` Jinja-free templates for compose and systemd units.
- `deploy/utils/` helpers for logging and file operations.
- 📌 Next Step Design Note
Minecraft One-Click Deployment Tool (demo1 branch)
下一阶段设计方向说明（中 / EN）
1. Current Status / 当前状态
EN

The demo1 branch has successfully validated the full deployment pipeline:

One-click install script (install.sh, setup.py)

Automatic Minecraft instance creation

Auto-generated docker-compose.yml

Auto-generated systemd service

Server boots successfully and is playable

This confirms that the overall architecture is viable.

中文

demo1 分支已经成功跑通 完整自动部署链路：

一键安装脚本（install.sh / setup.py）

自动创建 Minecraft 实例

自动生成 docker-compose.yml

自动生成并注册 systemd 服务

服务器可正常启动并进入世界

这说明 部署器整体架构是成立的。

2. Role of docker-compose.yml / 当前 yml 的定位
EN

The current docker-compose.yml template is designed to make the server run, not to fully describe all configurable capabilities.

environment:
  - EULA
  - VERSION
  - MEMORY
  {{ENV_BLOCK}}


This approach is acceptable for early demos, but cannot support future goals such as:

Interactive / guided deployment

Configuration encoding & decoding

Web panel capability mapping

Full historical Minecraft version support

中文

当前的 docker-compose.yml 模板目标是 “能跑起来”，而不是 “完整表达配置能力”：

environment:
  - EULA
  - VERSION
  - MEMORY
  {{ENV_BLOCK}}


这种方式在 demo1 阶段是合理的，但 无法支撑后续目标，例如：

引导式部署（交互提问）

配置串编码 / 反向还原

Web 面板能力映射

Minecraft 全历史版本适配

3. Identified Core Problems / 已识别的核心问题
Problem 1: ENV_BLOCK is a black box
问题 1：ENV_BLOCK 是黑箱

EN

The deployer cannot enumerate configurable options

No validation or version filtering is possible

Reverse generation (config → string) is impossible

中文

部署器无法枚举“有哪些配置项”

无法校验合法性、无法按版本裁剪

无法从已部署实例反向生成配置串

➡ Continuing this pattern will lead to unmaintainable complexity.

Problem 2: Minecraft settings are version-dependent
问题 2：Minecraft 设置强依赖版本

EN

server.properties and gamerules evolve across versions

Some options only exist in:

Beta / early releases

1.13+ data-driven era

Latest versions (1.20+)

Hard-coded if/else logic does not scale.

中文

server.properties / gamerule 随版本变化

部分设置只存在于：

远古版本

1.13+ 数据驱动时代

最新版本（1.20+）

简单的 if/else 逻辑 不可持续。

Problem 3: Goal is full historical version support
问题 3：目标是全历史版本支持

EN

The deployer aims to support all playable multiplayer versions, from early Beta / Release 1.0 up to modern versions.

This requires:

Version-aware configuration

Declarative metadata instead of procedural logic

中文

部署器目标明确：
支持 从最早可稳定联机的版本（Beta / Release 1.0）到最新版本。

这要求：

配置必须是 版本可裁剪的

必须使用 元数据驱动设计

4. Proposed Direction / 下一阶段总体方向
EN

Introduce a Single Source of Truth (SSOT):

A structured configuration field schema that defines
what can be configured, when, and for which versions.

This schema will drive:

docker-compose generation

ConfigModel validation

Interactive deployment

Configuration encoding / decoding

Web panel feature mapping

中文

引入一个 单一事实源（SSOT）：

一份结构化的 配置字段规范表，用于定义
可以配置什么、何时生效、适用于哪些版本。

这份规范将统一驱动：

docker-compose 生成

ConfigModel 校验

引导式部署

配置串编码 / 解码

Web 面板能力映射

5. Field Metadata Model / 字段元数据模型

Each configurable field must be described with metadata.

EN
name            # internal field name
docker_env      # itzg docker env variable
server_property # underlying server.properties key (if any)
type            # bool / int / enum / string
default         # default value
min_version     # minimum supported MC version
apply_stage     # startup | post_start
category        # gameplay / network / performance / admin

中文
name            # 内部字段名
docker_env      # itzg 镜像环境变量
server_property # 对应的 server.properties（如有）
type            # bool / int / enum / string
default         # 默认值
min_version     # 最低支持 MC 版本
apply_stage     # 启动时 / 启动后
category        # gameplay / network / performance / admin

6. Authoritative Data Sources / 权威数据来源
EN

The schema will be built from:

Official Minecraft server.properties documentation

itzg/docker-minecraft-server environment variable reference

Minecraft version history (for version gating)

中文

规范表将基于以下权威来源构建：

Minecraft 官方 server.properties 文档

itzg/docker-minecraft-server 官方环境变量文档

Minecraft 版本演进历史（用于版本裁剪）

7. Explicit Non-Goals / 当前阶段明确不做的事
EN

❌ Implement all rules immediately

❌ Embed logic in YAML

❌ Large if/else version branches

❌ Web panel integration (future phase)

中文

❌ 不一次性实现所有规则

❌ 不在 yml 中写逻辑

❌ 不写大规模 if/else

❌ 当前阶段不接入 Web 面板

8. Suggested Next Actions / 建议的下一步行动
EN

Create config-schema/ directory

Define:

server_properties.yaml

docker_envs.yaml

gameplay_rules.yaml (with version metadata)

Use schema to generate ConfigModel

中文

创建 config-schema/ 目录

定义：

server_properties.yaml

docker_envs.yaml

gameplay_rules.yaml（带版本元数据）

基于 schema 生成 ConfigModel

9. One-Sentence Summary / 一句话总结
EN

The system already deploys servers.
The next phase is about formalizing configuration, so every future feature becomes data-driven instead of refactoring-driven.

中文

当前系统已经能部署服务器；
下一阶段的核心不是加功能，而是 把配置模型定死，让未来所有功能都变成“填数据”，而不是“推翻重来”。
- `deploy/setup.py` entry point.

## Notes / caveats
- Paths and ports are generated; defaults: `/opt/mc-instances`, MC `25565`, panel `5000` (mapped from container).
- Update `WEB_PANEL_PATH` or template contents if your panel build lives elsewhere.
- This is a PoC; tighten security (RCON password, API keys, HTTPS) before production use.
