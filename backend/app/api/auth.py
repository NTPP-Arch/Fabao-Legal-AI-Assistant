"""注册、登录和当前用户认证接口。"""

from fastapi import APIRouter, Depends, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.exceptions import AppException
from app.core.security import create_access_token, get_password_hash, verify_password
from app.database import get_db
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.user import LoginRequest, RegisterRequest, TokenResponse, UserResponse


router = APIRouter(prefix="/auth", tags=["认证"])


@router.post(
    "/register",
    response_model=ApiResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="用户注册",
)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[UserResponse]:
    """校验唯一性并创建用户，返回不含密码的用户信息。"""
    email = str(payload.email).lower()
    duplicate = db.scalar(
        select(User).where(or_(User.username == payload.username, User.email == email))
    )
    if duplicate:
        field = "用户名" if duplicate.username == payload.username else "邮箱"
        raise AppException(f"{field}已被注册", status_code=409, code=409)

    user = User(
        username=payload.username,
        email=email,
        hashed_password=get_password_hash(payload.password),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise AppException("用户名或邮箱已被注册", status_code=409, code=409) from exc
    db.refresh(user)
    return ApiResponse(code=201, message="注册成功", data=user)


@router.post(
    "/login",
    response_model=ApiResponse[TokenResponse],
    summary="用户登录",
)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
) -> ApiResponse[TokenResponse]:
    """使用用户名或邮箱验证密码，并签发 Bearer JWT。"""
    account = payload.username.strip()
    user = db.scalar(
        select(User).where(or_(User.username == account, User.email == account.lower()))
    )
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise AppException("用户名或密码错误", status_code=401, code=401)

    token = create_access_token(str(user.id))
    return ApiResponse(data=TokenResponse(access_token=token))


@router.get(
    "/me",
    response_model=ApiResponse[UserResponse],
    summary="获取当前用户",
)
def me(current_user: User = Depends(get_current_user)) -> ApiResponse[UserResponse]:
    """返回当前 JWT 对应的用户资料。"""
    return ApiResponse(data=current_user)
