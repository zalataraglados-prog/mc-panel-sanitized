from fastapi import FastAPI, HTTPException

from deploy.claims_codec import Claims, decode_claims
from deploy.planner.planner import plan as plan_apply
from deploy.web.schemas import PlanRequest, PlanResponse
from deploy.web.review_adapter import review_to_dict


app = FastAPI(title="MC-Panel Web Review API")


@app.post("/deploy/plan", response_model=PlanResponse)
def plan_endpoint(payload: PlanRequest):
    try:
        if payload.import_string:
            claims = decode_claims(payload.import_string)
        else:
            claims = Claims(params=payload.params, profile=payload.profile)
        apply_plan = plan_apply(claims)
        return review_to_dict(apply_plan)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
