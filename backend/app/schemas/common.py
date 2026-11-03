"""统一 API 响应模型。"""

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict


DataT = TypeVar("DataT")


class ApiResponse(BaseModel, Generic[DataT]):
    """所有接口返回的统一外层结构。

    ``code`` 是业务码，HTTP 状态码仍由 FastAPI 正常表达；二者默认保持一致。
    """

    code: int = 200
    message: str = "success"
    data: DataT | None = None

    model_config = ConfigDict(from_attributes=True)
