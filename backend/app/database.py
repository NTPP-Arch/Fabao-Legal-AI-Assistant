"""SQLAlchemy 2.0 数据库连接、声明式基类和会话依赖。"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    """所有 SQLAlchemy 模型继承的 2.0 风格声明式基类。"""


# pool_pre_ping 可在 MySQL 长连接失效后自动检测并重连。
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=3600,
    future=True,
)

# expire_on_commit=False 便于接口在提交后直接序列化已刷新对象。
SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """FastAPI 数据库依赖：请求结束后无论成功失败都关闭会话。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
