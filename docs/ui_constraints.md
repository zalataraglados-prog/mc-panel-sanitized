# UI Constraints (Phase 14) / UI 约束（Phase 14）

This document defines non-negotiable UI constraints.
本文档定义 UI 的不可违背约束。

## Prohibited / 禁止事项

- Do not bypass Review.
- Do not bypass Execution Plan.
- Do not write configuration files directly.
- Do not apply recommendations automatically.
- Do not allow UI to modify Planner decisions.

- 不得绕过 Review。
- 不得绕过 Execution Plan。
- 不得直接写配置文件。
- 不得自动应用推荐。
- UI 不得影响 Planner 决策。

## Required Displays / 必须展示

- Review level (allow / warn / block).
- Warning and block reasons.
- Recommendations with explanations.
- Execution Plan (dry-run).

- Review 级别（allow / warn / block）。
- 警告与阻拦原因。
- 推荐项与解释。
- Execution Plan（dry-run）。

## Required Controls / 必须交互

- Toggle or prompt to confirm when Review is warn.
- Explicit stop when Review is block.
- Ability to copy/export Claims String (no auto apply).

- Review 为 warn 时必须确认。
- Review 为 block 时必须停止。
- 支持复制/导出 Claims String（禁止自动应用）。

## Template Usage / 模板使用

- Templates must be fetched from the official registry.
- UI must show template source and parameters before apply.

- 模板必须来自官方仓库。
- UI 必须在应用前展示模板来源与参数。

## Interaction Rules / 交互规则

- If Review is block, UI must stop execution.
- If Review is warn, UI must require explicit user confirmation.
- Apply must always follow Execution Plan in order.

- Review 为 block 时必须停止执行。
- Review 为 warn 时必须明确确认。
- Apply 必须严格按 Execution Plan 顺序执行。
