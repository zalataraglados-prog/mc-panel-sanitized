from __future__ import annotations

from typing import Mapping

TRANSLATIONS = {
    "en": {
        "category_heavy": {
            "message": "Multiple {category} parameters were changed; please consider the overall impact.",
            "hint": "Review the category adjustments before proceeding.",
        },
        "medium_risk_parameter": {
            "message": "Medium-risk parameter '{param}' deviates from its default.",
        },
        "high_risk_parameter": {
            "message": "High-risk parameter '{param}' deviates from its default.",
        },
        "novice_override": {
            "message": "Novice-sensitive parameter '{param}' was explicitly set.",
        },
        "capacity_block": {
            "message": "Configured memory is insufficient for the expected load.",
        },
        "capacity_warn": {
            "message": "Configured memory may be insufficient for the expected load.",
        },
        "scope_conflict": {
            "message": "Parameter '{param}' conflicts with the current scope or edition.",
        },
        "stack_invalid": {
            "message": "Unknown server stack type specified.",
        },
        "stack_param_conflict": {
            "message": "Some selected parameters are not supported by the chosen stack.",
        },
        "bedrock_param_not_supported": {
            "message": "This parameter is not applicable to Bedrock Edition.",
        },
        "range_violation": {
            "message": "Value for '{param}' is outside the recommended range.",
        },
        "type_invalid": {
            "message": "Value for '{param}' has an invalid type.",
        },
    },
    "zh": {
        "category_heavy": {
            "message": "多个 {category} 参数被修改，请检查整体影响。",
            "hint": "继续之前先确认这类参数的联动效果。",
        },
        "medium_risk_parameter": {
            "message": "中风险参数 '{param}' 偏离默认值。",
        },
        "high_risk_parameter": {
            "message": "高风险参数 '{param}' 偏离默认值。",
        },
        "novice_override": {
            "message": "针对初学者敏感参数 '{param}' 进行了显式设置。",
        },
        "capacity_block": {
            "message": "当前内存配置无法满足预计负载。",
        },
        "capacity_warn": {
            "message": "当前内存配置可能不足以应对预计负载。",
        },
        "scope_conflict": {
            "message": "参数 '{param}' 与当前作用域或版本冲突。",
        },
        "stack_invalid": {
            "message": "指定的服务器栈类型未知。",
        },
        "stack_param_conflict": {
            "message": "部分参数与当前服务器栈不兼容。",
        },
        "bedrock_param_not_supported": {
            "message": "该参数不适用于 Bedrock Edition。",
        },
        "range_violation": {
            "message": "参数 '{param}' 的值超出推荐范围。",
        },
        "type_invalid": {
            "message": "参数 '{param}' 的类型不合法。",
        },
    },
}


def translate_message(code: str, params: Mapping[str, str] | None, default: str, language: str) -> str:
    mappings = TRANSLATIONS.get(language, TRANSLATIONS["en"])
    entry = mappings.get(code)
    if not entry:
        return default
    template = entry.get("message")
    if not template:
        return default
    if params:
        return template.format(**params)
    return template


def translate_hint(code: str, default: str, language: str) -> str:
    mappings = TRANSLATIONS.get(language, TRANSLATIONS["en"])
    entry = mappings.get(code)
    if not entry:
        return default
    return entry.get("hint", default)
