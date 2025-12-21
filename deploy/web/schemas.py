from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PlanRequest(BaseModel):
    profile: str = Field(default="normal")
    params: Dict[str, Any] = Field(default_factory=dict)
    import_string: Optional[str] = Field(default=None)


class CapabilityReview(BaseModel):
    id: str
    status: str
    message: Optional[str] = None


class ReviewMessage(BaseModel):
    code: str
    message: str
    hint: Optional[str] = None


class ReviewMeta(BaseModel):
    review_version: int = 1
    planner_version: Optional[str] = None
    knowledge_base_version: Optional[str] = None


class PlanResponse(BaseModel):
    level: str
    capabilities: List[CapabilityReview]
    warnings: List[ReviewMessage]
    blocks: List[ReviewMessage]
    meta: ReviewMeta
