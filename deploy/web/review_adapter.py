def _message_to_dict(obj, *, default_code: str) -> dict:
    code = getattr(obj, "code", default_code)
    message = getattr(obj, "message", None)
    if message is None:
        message = str(obj)
    return {"code": code, "message": message}


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

    return {
        "level": apply_plan.summary.level,
        "capabilities": capabilities,
        "warnings": warnings,
        "blocks": blocks,
        "meta": {
            "review_version": 1,
            "planner_version": getattr(apply_plan, "planner_version", None),
        },
    }
