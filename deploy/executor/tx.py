"""
Execution Transaction Context (v1.0)

Purpose:
- Define a clear execution boundary
- Track execution progress
- Provide deterministic failure reporting
- Prepare hooks for future rollback / resume

This is NOT a full transaction system.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
import uuid
import time


class TxState(str, Enum):
    INIT = "init"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass
class TxStep:
    name: str
    started_at: Optional[float] = None
    finished_at: Optional[float] = None
    error: Optional[str] = None


@dataclass
class ExecutionTx:
    """
    Execution transaction context.
    """

    tx_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    state: TxState = TxState.INIT
    steps: List[TxStep] = field(default_factory=list)
    started_at: Optional[float] = None
    finished_at: Optional[float] = None

    # ───────────── lifecycle ─────────────

    def start(self):
        self.state = TxState.RUNNING
        self.started_at = time.time()

    def succeed(self):
        self.state = TxState.SUCCEEDED
        self.finished_at = time.time()

    def fail(self, error: str):
        self.state = TxState.FAILED
        self.finished_at = time.time()
        if self.steps:
            self.steps[-1].error = error

    # ───────────── step control ─────────────

    def begin_step(self, name: str):
        step = TxStep(name=name, started_at=time.time())
        self.steps.append(step)

    def end_step(self):
        if not self.steps:
            return
        self.steps[-1].finished_at = time.time()