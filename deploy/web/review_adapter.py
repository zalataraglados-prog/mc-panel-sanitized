def _message_to_dict(obj, *, default_code: str) -> dict:
    code = getattr(obj, "code", default_code)
    message = getattr(obj, "message", None)
    if message is None:
        message = str(obj)
    hint = getattr(obj, "hint", None)
    payload = {"code": code, "message": message}
    param = getattr(obj, "param", None)
    taxonomy = getattr(obj, "taxonomy", None)
    if param:
        payload["param"] = param
    if taxonomy:
        payload["taxonomy"] = taxonomy
    if hint:
        payload["hint"] = hint
    return payload


def review_to_dict(apply_plan) -> dict:
    """
    Convert ApplyPlan into a stable JSON review structure.
    """

    capabilities = []
    for result in apply_plan.capability_results:
        capabilities.append(
            {
                "id": result.capability_id,
                "status": result.status,
                "message": getattr(result, "message", None),
            }
        )

    warnings = [
        _message_to_dict(w, default_code="WARNING") for w in getattr(apply_plan, "warnings", [])
    ]
    blocks = [
        _message_to_dict(b, default_code="BLOCK") for b in getattr(apply_plan, "blocks", [])
    ]
    recommendations = []
    for rec in getattr(apply_plan, "recommendations", []):
        payload = {
            "param": getattr(rec, "param", None),
            "suggested": getattr(rec, "suggested", None),
            "reason": getattr(rec, "reason", None),
            "taxonomy": getattr(rec, "taxonomy", None),
        }
        recommendations.append(payload)

    return {
        "level": apply_plan.summary.level,
        "capabilities": capabilities,
        "warnings": warnings,
        "blocks": blocks,
        "recommendations": recommendations,
        "meta": {
            "review_version": 1,
            "planner_version": getattr(apply_plan, "planner_version", None),
            "knowledge_base_version": getattr(apply_plan, "knowledge_base_version", None),
            "imported_claims": getattr(apply_plan, "imported_claims", None),
        },
    }
