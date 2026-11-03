"""认证模块的 Pydantic V2 数据模型。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    """用户注册请求。"""

    username: str = Field(..., min_length=3, max_length=50, description="登录用户名")
    email: EmailStr = Field(..., max_length=100)
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        """去除首尾空格并限制为常见的用户名字符。"""
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("用户名不能为空")
        if not all(char.isalnum() or char in "_-" for char in cleaned):
            raise ValueError("用户名只能包含中文、字母、数字、下划线或短横线")
        return cleaned


class LoginRequest(BaseModel):
    """登录请求；username 字段同时接受用户名或邮箱。"""

    username: str = Field(..., min_length=1, max_length=100, description="用户名或邮箱")
    password: str = Field(..., min_length=1, max_length=128)


class UserResponse(BaseModel):
    """对外返回的用户信息，绝不包含密码哈希。"""

    id: int
    username: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """JWT 登录响应。"""

    access_token: str
    token_type: str = "bearer"
