# MC Panel 项目结构

## 项目概览

MC Panel 是一个 Minecraft 部署前的配置裁决引擎，运行期面板为可选组件。项目主要由 Python 后端（FastAPI）、前端页面（Vite构建）以及 Python 部署 CLI 工具组成。

## 详细结构

```text
mc-panel/
│
├── backend/                           # 后端代码（Python + FastAPI）
│   │
│   ├── data/                          # 数据存储目录
│   │   └── users.json                 # 用户数据
│   │
│   ├── routers/                       # API 路由端点
│   │   ├── auth.py                    # 认证 API
│   │   ├── bans.py                    # 封禁管理 API
│   │   ├── claims.py                  # 配置声明 API
│   │   ├── command.py                 # 命令执行 API
│   │   ├── control.py                 # 服务器启停控制 API
│   │   ├── instances.py               # 实例管理 API
│   │   ├── logs.py                    # 日志获取 API
│   │   ├── map.py                     # 地图插件 API
│   │   ├── metrics.py                 # 系统性能指标 API
│   │   ├── owners.py                  # 服主管理 API
│   │   ├── players.py                 # 玩家管理 API
│   │   ├── rcon.py                    # RCON 通信 API
│   │   ├── rules.py                   # 规则验证 API
│   │   ├── status.py                  # 服务器状态 API
│   │   ├── summary.py                 # 聚合信息 API
│   │   ├── templates.py               # 模板解析 API
│   │   └── users.py                   # 用户管理 API
│   │
│   ├── runtime/                       # 核心运行期服务与功能模块
│   │   ├── ansi.py                    # ANSI 颜色转义处理
│   │   ├── bans.py                    # 封禁名单读写逻辑
│   │   ├── cache.py                   # 缓存控制
│   │   ├── inventory.py               # 玩家背包管理 (离线NBT读取/在线RCON写入)
│   │   ├── log_paths.py               # 日志路径解析与管理
│   │   ├── log_streamer.py            # 日志流式传输功能
│   │   ├── map_provider.py            # 地图服务提供商适配 (Dynmap/BlueMap)
│   │   ├── mc_client.py               # Minecraft 原生协议客户端
│   │   ├── metrics.py                 # 性能指标收集服务
│   │   ├── nbt.py                     # NBT 数据解析工具
│   │   ├── owners.py                  # 服主验证与特权控制
│   │   ├── players_snapshot.py        # 玩家列表快照
│   │   ├── player_tracker.py          # 玩家在线状态跟踪
│   │   ├── rcon_client.py             # RCON 通信客户端
│   │   ├── service_control.py         # Systemctl 服务控制模块
│   │   └── status_snapshot.py         # 整体状态快照保存
│   │
│   ├── auth.py                        # 认证核心逻辑
│   ├── logging.py                     # 后端日志配置
│   ├── main.py                        # FastAPI 应用主入口
│   ├── models.py                      # 数据结构 (Pydantic 模型)
│   └── requirements.txt               # 后端 Python 依赖列表
│
├── deploy/                            # 部署 CLI 与执行引擎
│   │
│   ├── claims_codec/                  # 配置声明 (Claims) 编解码器
│   │   ├── compact.py                 # 紧凑编码压缩
│   │   ├── decode.py                  # 解码载入逻辑
│   │   ├── encode.py                  # 编码导出逻辑
│   │   └── minimal.py                 # 最小化编码转换
│   │
│   ├── compat/                        # 兼容性测试与矩阵
│   │   ├── modpack_index.py           # 整合包索引提取
│   │   └── modpack_matrix.py          # 模组与环境兼容矩阵判断
│   │
│   ├── core/                          # 部署核心组件
│   │   ├── composer.py                # Docker Compose 配置组装器
│   │   ├── config_model.py            # 基础环境配置模型
│   │   ├── deployer.py                # 应用级部署逻辑统筹
│   │   ├── environment.py             # 环境变量注入
│   │   ├── instance_creator.py        # 物理实例目录创建器
│   │   ├── instance_namer.py          # 实例命名规则处理器
│   │   ├── port_scanner.py            # 端口防冲突扫描
│   │   └── systemd_gen.py             # Systemd 守护进程服务生成
│   │
│   ├── deployment/                    # 部署状态与存储层
│   │   ├── model.py                   # 部署事务数据模型
│   │   └── store.py                   # 部署状态的本地存储
│   │
│   ├── dictionary/                    # 源字典与参考数据集
│   │   ├── compose_reference.yml      # 标准 Compose 模板片段
│   │   └── itzg_env_reference.yml     # itzg 相关通用环境变量字典
│   │
│   ├── executor/                      # 部署执行器与底层事务
│   │   ├── execution_plan.py          # 执行计划生成器 (Dry-run 支持)
│   │   ├── executor.py                # 执行器基类接口
│   │   ├── executor_planner.py        # 规则计划协调接口
│   │   ├── host_inspector.py          # 宿主机环境检测
│   │   ├── legacy_bridge.py           # 旧版部署桥接兼容
│   │   ├── plan_executor.py           # 执行计划的物理落盘
│   │   └── tx.py                      # 事务回滚处理
│   │
│   ├── mapper/                        # 配置映射转换
│   │   ├── legacy_config_mapper.py    # 老配置版本迁移映射
│   │   ├── mappings.py                # 基础字段映射
│   │   └── profiles.py                # 环境配置项处理
│   │
│   ├── planner/                       # 核心裁决与规划引擎
│   │   └── planner.py                 # 规则驱动的配置裁决与计算主逻辑
│   │
│   ├── templates/                     # 模板资源文件库
│   │   ├── bluemap.*.tpl              # BlueMap 插件系列配置模板
│   │   ├── config.json.tpl            # MC Panel 内部配置模板
│   │   ├── docker-compose.yml.tpl     # 容器编排基础模板
│   │   ├── dynmap.configuration.txt.tpl # Dynmap 配置模板
│   │   ├── mc-panel.service.tpl       # MC Panel 本体 Systemd 模板
│   │   └── minecraft.service.tpl      # Minecraft 实例 Systemd 模板
│   │
│   ├── tools/                         # 实用工具链
│   │   └── recommendation_sampling.py # 推荐配置采样分析工具
│   │
│   ├── utils/                         # 部署通用辅助模块
│   │   ├── cli_log.py                 # 命令行操作记录追踪
│   │   ├── file_helper.py             # 文件与目录操作辅助
│   │   └── logger.py                  # 统一部署日志组件
│   │
│   ├── web/                           # 交互层桥接
│   │   ├── app.py                     # CLI 应用流程核心控制
│   │   ├── i18n.py                    # 终端输出多语言切换
│   │   ├── review_adapter.py          # 安全审查结果转译适配
│   │   └── schemas.py                 # 数据展示/视图层数据结构
│   │
│   ├── capacity_guard.py              # 容量护栏限制保护 (如 JVM 内存保护)
│   ├── cli.py                         # Deploy 主入口
│   ├── context.py                     # 全局上下文管理
│   ├── dictionary_projection.py       # 实体字典映射注入
│   ├── loader.py                      # 规则加载器 (拉取远端 Catalog/Taxonomy)
│   ├── panel_manager.py               # Web 面板安装/卸载控制器
│   ├── phase12_validation.json        # 两阶段校验配置列表
│   ├── setup.py                       # Python 模块打包信息
│   ├── templates_registry.json        # 模板清单注册表
│   └── usability_overlay.py           # 可用性增量覆盖脚本
│
├── docs/                              # 工程文档与参考资料
│   ├── compatibility.md               # 组件兼容性要求说明
│   ├── mod_plugin_compat.md           # Mod 与插件特性冲突矩阵
│   └── ui_constraints.md              # 面板界面开发约束规范
│
├── frontend/                          # 前端工程 (Vite + React)
│   ├── dist/                          # 前端构建输出静态文件产物
│   │   ├── assets/                    # 构建出来的 JS/CSS 静态资源
│   │   └── index.html                 # 渲染主入口
│   ├── index.html                     # 源码入口 HTML
│   ├── package.json                   # NPM 依赖定义
│   ├── tsconfig.json                  # TypeScript 全局配置
│   └── vite.config.ts                 # Vite 构建脚本与插件配置
│
├── install.sh                         # Linux 一键极速部署与安装脚本
├── README.md                          # 库使用主说明文档
├── .gitignore                         # Git 忽略规则
├── deploy_report.txt                  # 部署过程执行摘要报告
├── backend.out.log                    # 面板后端标准输出日志
└── backend.err.log                    # 面板后端错误输出日志
```
