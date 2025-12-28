# UI Constraints (Phase 14)

This document defines non-negotiable UI constraints.

## Prohibited

- Do not bypass Review.
- Do not bypass Execution Plan.
- Do not write configuration files directly.
- Do not apply recommendations automatically.
- Do not allow UI to modify Planner decisions.

## Required Displays

- Review level (allow / warn / block).
- Warning and block reasons.
- Recommendations with explanations.
- Execution Plan (dry-run).

## Required Controls

- Toggle or prompt to confirm when Review is warn.
- Explicit stop when Review is block.
- Ability to copy/export Claims String (no auto apply).

## Template Usage

- Templates must be fetched from the official registry.
- UI must show template source and parameters before apply.

## Interaction Rules

- If Review is block, UI must stop execution.
- If Review is warn, UI must require explicit user confirmation.
- Apply must always follow Execution Plan in order.
