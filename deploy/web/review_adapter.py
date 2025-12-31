from deploy.web.i18n import translate_hint, translate_message


def _message_to_dict(obj, *, default_code: str, language: str) -> dict:
    code = getattr(obj, "code", default_code)
    raw_message = getattr(obj, "message", None)
    if raw_message is None:
        raw_message = str(obj)
    hint = getattr(obj, "hint", None)
    params = {"param": getattr(obj, "param", None), "category": getattr(obj, "taxonomy", {}).get("category") if getattr(obj, "taxonomy", None) else None}
    message = translate_message(code, params, raw_message, language)
    payload = {"code": code, "message": message}
    param = getattr(obj, "param", None)
    taxonomy = getattr(obj, "taxonomy", None)
    if param:
        payload["param"] = param
    if taxonomy:
        payload["taxonomy"] = taxonomy
    if hint:
        payload["hint"] = translate_hint(code, hint, language)
    return payload


def review_to_dict(apply_plan, *, language: str = "en") -> dict:
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
        _message_to_dict(w, default_code="WARNING", language=language) for w in getattr(apply_plan, "warnings", [])
    ]
    blocks = [
        _message_to_dict(b, default_code="BLOCK", language=language) for b in getattr(apply_plan, "blocks", [])
    ]
    recommendations = []
    for rec in getattr(apply_plan, "recommendations", []):
        reason = getattr(rec, "reason", None)
        translated_reason = translate_message(
            getattr(rec, "code", "RECOMMENDATION"),
            {"param": getattr(rec, "param", None)},
            reason or "",
            language,
        )
        payload = {
            "param": getattr(rec, "param", None),
            "suggested": getattr(rec, "suggested", None),
            "reason": translated_reason or reason,
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
