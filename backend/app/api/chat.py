"""AI 法律咨询接口。"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.exceptions import AppException
from app.database import get_db
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.user import User
from app.schemas.chat import (
    ChatReplyResponse,
    ConversationCreate,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
)
from app.schemas.common import ApiResponse
from app.services.ai_service import generate_legal_reply


router = APIRouter(prefix="/chat", tags=["AI法律咨询"])


def _get_owned_conversation(
    db: Session, conversation_id: int, user_id: int
) -> Conversation:
    """只查询当前用户拥有的对话，避免越权读取其他用户数据。"""
    conversation = db.scalar(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
    )
    if conversation is None:
        raise AppException("对话不存在", status_code=404, code=404)
    return conversation


@router.get(
    "/conversations",
    response_model=ApiResponse[list[ConversationResponse]],
    summary="获取对话列表",
)
def list_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[list[ConversationResponse]]:
    """按最近更新时间倒序返回当前用户的对话。"""
    conversations = list(
        db.scalars(
            select(Conversation)
            .where(Conversation.user_id == current_user.id)
            .order_by(Conversation.updated_at.desc(), Conversation.id.desc())
        ).all()
    )
    return ApiResponse(data=conversations)


@router.post(
    "/conversations",
    response_model=ApiResponse[ConversationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="新建对话",
)
def create_conversation(
    payload: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[ConversationResponse]:
    """创建一个空对话。"""
    conversation = Conversation(
        user_id=current_user.id,
        title=payload.title or "新建对话",
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return ApiResponse(code=201, message="创建成功", data=conversation)


@router.delete(
    "/conversations/{conversation_id}",
    response_model=ApiResponse[None],
    summary="删除对话",
)
def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[None]:
    """删除当前用户的对话及其消息。"""
    conversation = _get_owned_conversation(db, conversation_id, current_user.id)
    db.delete(conversation)
    db.commit()
    return ApiResponse(message="删除成功", data=None)


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=ApiResponse[list[MessageResponse]],
    summary="获取对话消息",
)
def list_messages(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[list[MessageResponse]]:
    """按时间顺序返回对话消息。"""
    _get_owned_conversation(db, conversation_id, current_user.id)
    messages = list(
        db.scalars(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc(), Message.id.asc())
        ).all()
    )
    return ApiResponse(data=messages)


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=ApiResponse[ChatReplyResponse],
    summary="发送法律咨询消息",
)
def send_message(
    conversation_id: int,
    payload: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[ChatReplyResponse]:
    """保存用户消息，调用 AI 服务并保存助手回复。"""
    conversation = _get_owned_conversation(db, conversation_id, current_user.id)

    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=payload.content,
    )
    db.add(user_message)
    db.flush()
    try:
        # 每个后端会话绑定一个 FastGPT chatId，追问时携带前文上下文。
        reply = generate_legal_reply(
            payload.content, chat_id=f"conversation-{conversation.id}"
        )
    except RuntimeError as exc:
        # AI 调用失败时整体回滚，用户消息不落库，前端可直接提示重试。
        raise AppException(f"AI 服务调用失败：{exc}", status_code=502, code=502) from exc
    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=reply,
    )
    db.add(assistant_message)
    # 显式更新时间，兼容 MySQL 5.7 对 DateTime server_onupdate 的差异。
    conversation.updated_at = datetime.now(timezone.utc)
    if conversation.title in (None, "新建对话"):
        conversation.title = payload.content[:100]
    db.commit()
    db.refresh(user_message)
    db.refresh(assistant_message)
    return ApiResponse(
        data=ChatReplyResponse(
            conversation_id=conversation.id,
            user_message=user_message,
            assistant_message=assistant_message,
        )
    )
