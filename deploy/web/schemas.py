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
    param: Optional[str] = None
    taxonomy: Optional[Dict[str, Any]] = None


class Recommendation(BaseModel):
    param: str
    suggested: Optional[Any] = None
    reason: Optional[str] = None
    taxonomy: Optional[Dict[str, Any]] = None


class ReviewMeta(BaseModel):
    review_version: int = 1
    planner_version: Optional[str] = None
    knowledge_base_version: Optional[str] = None
    imported_claims: Optional[bool] = None


class PlanResponse(BaseModel):
    level: str
    capabilities: List[CapabilityReview]
    warnings: List[ReviewMessage]
    blocks: List[ReviewMessage]
    recommendations: List[Recommendation] = Field(default_factory=list)
    meta: ReviewMeta


class DeploymentView(BaseModel):
    id: str
    status: str
    claims: Dict[str, Any]
    plan_review: Dict[str, Any]


class DecisionResponse(BaseModel):
    claims: Dict[str, Any]
    review: PlanResponse
    deployment: DeploymentView
