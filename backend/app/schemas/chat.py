"""AI 法律咨询模块的请求与响应模型。"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ConversationCreate(BaseModel):
    """新建对话请求。"""

    title: str | None = Field(default=None, max_length=100)

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str | None) -> str | None:
        """将空标题转成默认值，避免数据库保存无意义空白。"""
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class ConversationResponse(BaseModel):
    """对话摘要响应。"""

    id: int
    title: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageCreate(BaseModel):
    """发送消息请求。"""

    content: str = Field(..., min_length=1, max_length=20_000)

    @field_validator("content")
    @classmethod
    def normalize_content(cls, value: str) -> str:
        """清除消息首尾空白，阻止只发送空格。"""
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("消息内容不能为空")
        return cleaned


class MessageResponse(BaseModel):
    """消息响应。"""

    id: int
    conversation_id: int
    role: Literal["user", "assistant"]
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatReplyResponse(BaseModel):
    """发送消息后同时返回用户消息和模拟 AI 回复。"""

    conversation_id: int
    user_message: MessageResponse
    assistant_message: MessageResponse
