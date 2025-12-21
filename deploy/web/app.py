from fastapi import FastAPI, HTTPException

from deploy.claims_codec import Claims, decode_claims
from deploy.planner.planner import plan as plan_apply
from deploy.deployment.model import Deployment, DeploymentStatus
from deploy.web.schemas import DecisionResponse, PlanRequest, PlanResponse
from deploy.web.review_adapter import review_to_dict


app = FastAPI(title="MC-Panel Web Review API")


@app.post("/deploy/plan", response_model=PlanResponse)
def plan_endpoint(payload: PlanRequest):
    try:
        if payload.import_string:
            if payload.params or payload.profile != "normal":
                raise ValueError("import_string cannot be combined with params/profile")
            claims = decode_claims(payload.import_string)
        else:
            claims = Claims(params=payload.params, profile=payload.profile)
        apply_plan = plan_apply(claims)
        if getattr(claims, "imported_from_string", False):
            setattr(apply_plan, "imported_claims", True)
        return review_to_dict(apply_plan)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/deploy/decision", response_model=DecisionResponse)
def decision_endpoint(payload: PlanRequest):
    try:
        if payload.import_string:
            if payload.params or payload.profile != "normal":
                raise ValueError("import_string cannot be combined with params/profile")
            claims = decode_claims(payload.import_string)
        else:
            claims = Claims(params=payload.params, profile=payload.profile)

        apply_plan = plan_apply(claims)
        if getattr(claims, "imported_from_string", False):
            setattr(apply_plan, "imported_claims", True)
        review = review_to_dict(apply_plan)

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
