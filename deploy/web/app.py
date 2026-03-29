import os

from fastapi import FastAPI, HTTPException

from deploy.claims_codec import Claims, decode_claims
from deploy.planner.planner import plan as plan_apply
from deploy.deployment.model import Deployment, DeploymentStatus
from deploy.web.schemas import (
    DeploymentView,
    DecisionResponse,
    PlanRequest,
    PlanResponse,
)
from deploy.web.review_adapter import review_to_dict
from deploy.executor.host_inspector import HostInspector


app = FastAPI(title="MC-Panel Web Review API")
inspector = HostInspector()


@app.post("/deploy/plan", response_model=PlanResponse)
def plan_endpoint(payload: PlanRequest):
    try:
        if payload.import_string:
            if payload.params or payload.profile != "normal":
                raise ValueError("import_string cannot be combined with params/profile")
            params = decode_claims(payload.import_string)
            claims = Claims(params=params, profile="normal", imported=True)
        else:
            claims = Claims(params=payload.params, profile=payload.profile)
        apply_plan = plan_apply(claims)
        if getattr(claims, "imported_from_string", False):
            setattr(apply_plan, "imported_claims", True)
        return review_to_dict(apply_plan, language=payload.language)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/deploy/decision", response_model=DecisionResponse)
def decision_endpoint(payload: PlanRequest):
    try:
        if payload.import_string:
            if payload.params or payload.profile != "normal":
                raise ValueError("import_string cannot be combined with params/profile")
            params = decode_claims(payload.import_string)
            claims = Claims(params=params, profile="normal", imported=True)
        else:
            claims = Claims(params=payload.params, profile=payload.profile)

        apply_plan = plan_apply(claims)
        if getattr(claims, "imported_from_string", False):
            setattr(apply_plan, "imported_claims", True)
        review = review_to_dict(apply_plan, language=payload.language)

        deployment = Deployment(
            claims={"profile": claims.profile, "params": claims.params},
            plan_review=review,
            status=DeploymentStatus.PLANNED,
        )

        return {
            "claims": {"profile": claims.profile, "params": claims.params},
            "review": review,
            "deployment": deployment.to_dict(),
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/deploy/instances")
def instances_endpoint(base_dir: str = "/opt/mc-instances"):
    os.environ["MC_PANEL_BASE_DIR"] = base_dir
    result = inspector.list_instances()
    if not result.get("ok"):
        raise HTTPException(status_code=404, detail=result.get("details"))
    return result
