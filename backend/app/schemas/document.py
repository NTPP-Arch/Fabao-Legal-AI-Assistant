"""文书生成模块的 Pydantic V2 数据模型。"""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


DocumentType = Literal["起诉状", "答辩状", "律师函", "授权委托书", "合同模板"]


class DocumentGenerateRequest(BaseModel):
    """文书生成请求。"""

    doc_type: DocumentType
    form_data: dict[str, Any] = Field(default_factory=dict)


class DocumentResponse(BaseModel):
    """文书记录响应。"""

    id: int
    user_id: int
    doc_type: str
    form_data: dict[str, Any]
    generated_content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
