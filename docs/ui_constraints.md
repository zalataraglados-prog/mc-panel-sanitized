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

## Interaction Rules

- If Review is block, UI must stop execution.
- If Review is warn, UI must require explicit user confirmation.
- Apply must always follow Execution Plan in order.
