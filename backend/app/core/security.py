"""密码哈希和 JWT 认证工具。"""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt
from passlib.context import CryptContext

from app.config import settings


# bcrypt 只保存不可逆哈希；明文密码不会进入数据库或日志。
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码是否匹配数据库中的 bcrypt 哈希。"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """使用 bcrypt 生成密码哈希。"""
    return pwd_context.hash(password)


def create_access_token(
    subject: str, expires_delta: timedelta | None = None, **extra_claims: Any
) -> str:
    """创建包含用户标识和过期时间的 JWT。"""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload = {"sub": subject, "exp": expire, **extra_claims}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
