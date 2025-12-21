import os
from dataclasses import dataclass

from deploy.executor.legacy_bridge import apply_legacy_config
from deploy.executor.tx import ExecutionTx
from deploy.core.config_model import ConfigModel
from deploy.mapper.legacy_config_mapper import map_claims_to_legacy_config


class ExecutorError(Exception):
    pass


@dataclass
class ExecutionResult:
    tx: ExecutionTx


class Executor:
    def __init__(self, *, ctx=None):
        self.ctx = ctx

    def apply(self, *, context, claims, plan_review):
        if not hasattr(plan_review, "summary"):
            raise ExecutorError("ApplyPlan is required for execution")
        if plan_review.summary.level == "block":
            raise ExecutorError("ApplyPlan is blocked")

        panel_src_dir = "/opt/mc-panel-sanitized/web-panel"

        config_path = os.path.join(context.instance_dir, "config.json")
        cfg = ConfigModel(path=config_path)
        cfg.data = ConfigModel.generate_default(
            context.instance_name,
            context.instance_dir,
            context.mc_port,
            context.panel_port,
        )
        cfg.data.setdefault("panel", {})
        cfg.data["panel"]["build_path"] = panel_src_dir

        legacy_config = map_claims_to_legacy_config(
            claims=claims,
            base_config=cfg.data,
            apply_plan=plan_review,
        )
        cfg.data = legacy_config
        cfg.data.setdefault("panel", {})
        cfg.data["panel"]["build_path"] = panel_src_dir
        cfg.save()

        tx = ExecutionTx()
        tx.start()

        try:
            tx.begin_step("apply_legacy_config")

            apply_legacy_config(
                cfg=cfg,
                ctx=context,
            )

            tx.end_step()
            tx.succeed()
            return ExecutionResult(tx=tx)

        except Exception as e:
            tx.fail(str(e))
            raise ExecutorError(f"Execution failed: {e}") from e

    def execute(self, *, apply_plan, cfg):
        """
        Legacy compatibility path.
        """
        if self.ctx is None:
            raise ExecutorError("Legacy executor requires ctx")
        if apply_plan.summary.level == "block":
            raise ExecutorError("ApplyPlan is blocked")

        tx = ExecutionTx()
        tx.start()

        try:
            tx.begin_step("apply_legacy_config")

            apply_legacy_config(
                cfg=cfg,
                ctx=self.ctx,
            )

            tx.end_step()
            tx.succeed()
            return tx

        except Exception as e:
            tx.fail(str(e))
            raise ExecutorError(f"Execution failed: {e}") from e
