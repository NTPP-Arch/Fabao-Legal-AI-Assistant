"""文书生成业务服务。"""

from typing import Any

from app.services.ai_service import ai_client, strip_cite_markers

_SUPPORTED_TYPES = {"起诉状", "答辩状", "律师函", "授权委托书", "合同模板"}


def _build_prompt(doc_type: str, form_data: dict[str, Any]) -> str:
    """把表单字段拼成自然语言描述，便于工作流分类到文书生成分支。"""
    details = "；".join(
        f"{key}：{value}" for key, value in form_data.items() if value not in (None, "")
    )
    if not details:
        return f"帮我写一份{doc_type}"
    return f"帮我写一份{doc_type}。相关信息：{details}"


def generate_document(doc_type: str, form_data: dict[str, Any]) -> str:
    """调用 FastGPT 文书生成分支生成文书正文。"""
    if doc_type not in _SUPPORTED_TYPES:
        raise ValueError(f"不支持的文书类型：{doc_type}")
    return strip_cite_markers(
        ai_client.generate_reply(_build_prompt(doc_type, form_data))
    )
