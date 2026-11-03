"""应用自定义异常及错误码。"""

from typing import Any


class AppException(Exception):
    """可安全返回给客户端的业务异常。"""

    def __init__(
        self,
        message: str,
        *,
        status_code: int = 400,
        code: int | None = None,
        data: Any = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code or status_code
        self.data = data
