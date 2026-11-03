"""FastAPI 公共依赖：数据库会话和当前登录用户。"""

from collections.abc import Generator

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.core.exceptions import AppException
from app.database import get_db
from app.models.user import User


# 登录接口使用 JSON 请求，因此采用纯 Bearer 安全方案，Swagger 可直接填写 JWT。
bearer_scheme = HTTPBearer(auto_error=False)


def get_db_session() -> Generator[Session, None, None]:
    """兼容性别名，统一从 database 模块提供数据库会话。"""
    yield from get_db()


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """解析 Bearer JWT 并加载用户；失败统一返回 401 业务异常。"""
    credentials_error = AppException(
        "登录凭证无效或已过期", status_code=401, code=401
    )
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise credentials_error

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        subject = payload.get("sub")
        if not subject:
            raise credentials_error
        user_id = int(subject)
    except (JWTError, TypeError, ValueError) as exc:
        raise credentials_error from exc

    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise credentials_error
    return user
