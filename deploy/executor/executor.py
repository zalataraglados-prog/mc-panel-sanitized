from deploy.executor.legacy_bridge import apply_legacy_config
from deploy.executor.tx import ExecutionTx


class ExecutorError(Exception):
    pass


class Executor:
    def __init__(self, *, ctx):
        self.ctx = ctx

    def execute(self, *, apply_plan, cfg):
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
