"""文书生成与历史记录接口。"""

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.exceptions import AppException
from app.database import get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.document import DocumentGenerateRequest, DocumentResponse
from app.services.document_service import generate_document


router = APIRouter(prefix="/documents", tags=["文书生成"])


@router.post(
    "/generate",
    response_model=ApiResponse[DocumentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="生成法律文书",
)
def generate(
    payload: DocumentGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[DocumentResponse]:
    """调用 AI 服务生成文书并保存记录。"""
    try:
        content = generate_document(payload.doc_type, payload.form_data)
    except ValueError as exc:
        raise AppException(str(exc), status_code=400, code=400) from exc
    except RuntimeError as exc:
        # AI 调用失败时不落库，前端可直接提示重试。
        raise AppException(f"AI 服务调用失败：{exc}", status_code=502, code=502) from exc

    document = Document(
        user_id=current_user.id,
        doc_type=payload.doc_type,
        form_data=payload.form_data,
        generated_content=content,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return ApiResponse(code=201, message="文书生成成功", data=document)


@router.get(
    "/list",
    response_model=ApiResponse[list[DocumentResponse]],
    summary="获取文书历史",
)
def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[list[DocumentResponse]]:
    """返回当前用户的文书生成记录。"""
    documents = list(
        db.scalars(
            select(Document)
            .where(Document.user_id == current_user.id)
            .order_by(Document.created_at.desc(), Document.id.desc())
        ).all()
    )
    return ApiResponse(data=documents)


@router.get(
    "/{document_id}",
    response_model=ApiResponse[DocumentResponse],
    summary="获取文书详情",
)
def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[DocumentResponse]:
    """按 ID 获取当前用户的文书，拒绝跨用户访问。"""
    document = db.scalar(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id,
        )
    )
    if document is None:
        raise AppException("文书记录不存在", status_code=404, code=404)
    return ApiResponse(data=document)
