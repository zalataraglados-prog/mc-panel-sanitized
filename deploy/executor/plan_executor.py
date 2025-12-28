from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Dict, List

from deploy.executor.execution_plan import ExecutionPlan
from deploy.executor.host_inspector import HostInspector


@dataclass
class ExecutionStep:
    name: str
    ok: bool
    details: str = ""


@dataclass
class ExecutionResult:
    ok: bool
    steps: List[ExecutionStep] = field(default_factory=list)


class ExecutionPlanExecutor:
    def __init__(self, inspector: HostInspector | None = None):
        self.inspector = inspector or HostInspector()

    def _check_precondition(self, precondition) -> ExecutionStep:
        check_type = precondition.type
        value = precondition.value
        if check_type == "path_exists":
            result = self.inspector.check_path_exists(value)
        elif check_type == "path_writable":
            result = self.inspector.check_path_writable(value)
        elif check_type == "port_free":
            result = self.inspector.check_port_free(int(value))
        elif check_type == "docker_available":
            result = self.inspector.check_docker_available()
        elif check_type == "systemd_available":
            result = self.inspector.check_systemd_available()
        elif check_type == "capacity_sufficient":
            try:
                memory = float(value.get("memory_gb"))
                required = float(value.get("required_gb"))
                ok = memory >= required and memory >= 2.0
                details = f"memory_gb={memory} required_gb={required}"
            except Exception:
                return ExecutionStep(
                    name="precondition:capacity_sufficient",
                    ok=False,
                    details="invalid capacity payload",
                )
            return ExecutionStep(
                name="precondition:capacity_sufficient",
                ok=ok,
                details=details,
            )
        else:
            return ExecutionStep(
                name=f"precondition:{check_type}",
                ok=False,
                details="unknown precondition type",
            )
        return ExecutionStep(
            name=f"precondition:{check_type}",
            ok=bool(result.get("ok")),
            details=str(result.get("details", "")),
        )

    def _execute_action(self, action) -> ExecutionStep:
        action_type = action.type
        params: Dict[str, Any] = action.params or {}

        if action_type == "mkdir":
            path = params.get("path")
            if not path:
                return ExecutionStep(name="action:mkdir", ok=False, details="missing path")
            os.makedirs(path, exist_ok=True)
            return ExecutionStep(name="action:mkdir", ok=True, details=path)

        if action_type == "write_file":
            path = params.get("path")
            content = params.get("content")
            template = params.get("template")
            if template and content is None:
                context = params.get("context", {})
                content = self._render_template(template, context)
            if path is None or content is None:
                return ExecutionStep(
                    name="action:write_file",
                    ok=False,
                    details="missing path/content",
                )
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(content)
            return ExecutionStep(name="action:write_file", ok=True, details=path)

        if action_type == "symlink":
            source = params.get("source")
            target = params.get("target")
            if not source or not target:
                return ExecutionStep(name="action:symlink", ok=False, details="missing source/target")
            if os.path.lexists(target):
                os.remove(target)
            os.symlink(source, target)
            return ExecutionStep(name="action:symlink", ok=True, details=f"{source} -> {target}")

        return ExecutionStep(
            name=f"action:{action_type}",
            ok=False,
            details="unsupported action type",
        )

    def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates"))
        template_path = os.path.join(base_dir, template_name)
        if not os.path.exists(template_path):
            raise RuntimeError(f"Template not found: {template_name}")
        with open(template_path, "r", encoding="utf-8") as handle:
            raw = handle.read()
        rendered = raw
        for key, value in context.items():
            rendered = rendered.replace(f"{{{{{key}}}}}", str(value))
        return rendered

    def execute(self, plan: ExecutionPlan) -> ExecutionResult:
        steps: List[ExecutionStep] = []

        for pre in plan.preconditions:
            step = self._check_precondition(pre)
            steps.append(step)
            if pre.required and not step.ok:
                return ExecutionResult(ok=False, steps=steps)

        for action in plan.actions:
            step = self._execute_action(action)
            steps.append(step)
            if not step.ok:
                return ExecutionResult(ok=False, steps=steps)

        return ExecutionResult(ok=True, steps=steps)
