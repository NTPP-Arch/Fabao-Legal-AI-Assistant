"""合同上传与审查模块的数据模型。"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ContractResponse(BaseModel):
    """合同记录响应。"""

    id: int
    user_id: int
    file_name: str
    file_path: str
    original_text: str
    review_result: dict[str, Any] | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
