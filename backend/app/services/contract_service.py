"""合同审查业务服务。"""

import json
import re
from typing import Any

from app.services.ai_service import ai_client, strip_cite_markers

_LEVEL_CN = {"high": "高", "medium": "中", "low": "低"}

# 风险等级权重：按高/中/低风险条数加权重算总分，满分 100。
_SCORE_WEIGHTS = {"high": 15, "medium": 8, "low": 3}


def _to_int(value: Any) -> int:
    """宽容地转整数，模型输出异常时按 0 处理。"""
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _extract_json(text: str) -> dict[str, Any]:
    """从模型输出中提取 JSON：剥离 ```json 围栏，截取首尾大括号之间的内容。"""
    cleaned = text.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)```", cleaned, re.DOTALL)
    if fenced:
        cleaned = fenced.group(1).strip()
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start == -1 or end <= start:
        raise ValueError("模型输出中未找到 JSON 对象")
    return json.loads(cleaned[start : end + 1])


def _recompute_score(stats: dict[str, Any]) -> int:
    """按 15/8/3 权重从风险条数重算总分，保证与条数一致、不依赖模型自报分值。"""
    score = sum(
        _SCORE_WEIGHTS[key] * _to_int(stats.get(key)) for key in _SCORE_WEIGHTS
    )
    return min(score, 100)


def review_contract(original_text: str) -> dict[str, object]:
    """调用 FastGPT 合同审查分支，并把模型 JSON 归一化为统一结构。

    归一化目标：``risk_level``/``risk_items[].level`` 统一为中文「高/中/低」，
    ``risk_score`` 按 15/8/3 权重由 ``risk_stats`` 重算，前端按固定结构渲染。
    """
    raw = ai_client.generate_reply(f"帮我审查这份合同：\n{original_text}")
    try:
        data = _extract_json(strip_cite_markers(raw))
    except (ValueError, json.JSONDecodeError) as exc:
        # 解析失败时保留原文，前端仍可展示模型输出。
        return {
            "risk_level": "中",
            "risk_score": None,
            "summary": raw,
            "risk_items": [],
            "parse_error": str(exc),
        }

    items = data.get("risks") or data.get("risk_items") or []
    risk_items: list[dict[str, str]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        risk_items.append(
            {
                "level": _LEVEL_CN.get(str(item.get("level", "")).lower(), "低"),
                "category": str(item.get("category") or ""),
                "clause": str(item.get("clause") or ""),
                "analysis": str(item.get("analysis") or ""),
                "suggestion": str(item.get("suggestion") or ""),
                "law": str(item.get("law") or ""),
            }
        )

    stats = data.get("risk_stats") or {}
    high = _to_int(stats.get("high"))
    medium = _to_int(stats.get("medium"))
    low = _to_int(stats.get("low"))
    if high > 0:
        risk_level = "高"
    elif medium > 0:
        risk_level = "中"
    else:
        risk_level = "低"

    return {
        "risk_level": risk_level,
        "risk_score": _recompute_score(stats) if stats else data.get("risk_score"),
        "summary": str(data.get("suggestion") or ""),
        "risk_stats": {"高": high, "中": medium, "低": low},
        "risk_items": risk_items,
    }
