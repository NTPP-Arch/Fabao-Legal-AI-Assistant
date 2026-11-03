"""合同文件上传、解析和审查接口。"""

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.core.dependencies import get_current_user
from app.core.exceptions import AppException
from app.database import get_db
from app.models.contract import Contract
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.contract import ContractResponse
from app.services.contract_service import review_contract
from app.utils.file_handler import FileParseError, extract_text


router = APIRouter(prefix="/contracts", tags=["合同审查"])
ALLOWED_SUFFIXES = {".docx", ".pdf"}
CHUNK_SIZE = 64 * 1024


@router.post(
    "/upload",
    response_model=ApiResponse[ContractResponse],
    status_code=status.HTTP_201_CREATED,
    summary="上传合同文件",
)
async def upload_contract(
    file: UploadFile = File(..., description=".docx 或 .pdf 合同文件"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[ContractResponse]:
    """校验扩展名和大小，使用随机文件名保存后提取文本。"""
    original_name = Path(file.filename or "").name
    suffix = Path(original_name).suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise AppException("仅支持 .docx 和 .pdf 文件", status_code=400, code=400)
    if not original_name:
        raise AppException("文件名不能为空", status_code=400, code=400)

    upload_dir = settings.upload_path
    upload_dir.mkdir(parents=True, exist_ok=True)
    saved_path = upload_dir / f"{uuid4().hex}{suffix}"
    size = 0
    try:
        with saved_path.open("wb") as output:
            while chunk := await file.read(CHUNK_SIZE):
                size += len(chunk)
                if size > settings.max_upload_size:
                    raise AppException("文件大小不能超过 10MB", status_code=413, code=413)
                output.write(chunk)

        try:
            original_text = extract_text(saved_path)
        except FileParseError as exc:
            raise AppException(str(exc), status_code=400, code=400) from exc

        contract = Contract(
            user_id=current_user.id,
            file_name=original_name[:255],
            file_path=str(saved_path),
            original_text=original_text,
        )
        db.add(contract)
        db.commit()
        db.refresh(contract)
        return ApiResponse(code=201, message="合同上传成功", data=contract)
    except AppException:
        if saved_path.exists():
            saved_path.unlink()
        raise
    except OSError as exc:
        if saved_path.exists():
            saved_path.unlink()
        raise AppException("文件保存失败", status_code=500, code=500) from exc
    finally:
        await file.close()


@router.post(
    "/review/{contract_id}",
    response_model=ApiResponse[ContractResponse],
    summary="执行合同审查",
)
def review(
    contract_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[ContractResponse]:
    """对当前用户已经上传的合同执行 AI 审查。"""
    contract = db.scalar(
        select(Contract).where(
            Contract.id == contract_id,
            Contract.user_id == current_user.id,
        )
    )
    if contract is None:
        raise AppException("合同记录不存在", status_code=404, code=404)

    try:
        contract.review_result = review_contract(contract.original_text)
    except RuntimeError as exc:
        # AI 调用失败时合同记录保持原状，前端可直接提示重试。
        raise AppException(f"AI 服务调用失败：{exc}", status_code=502, code=502) from exc
    db.commit()
    db.refresh(contract)
    return ApiResponse(message="合同审查完成", data=contract)


@router.get(
    "/list",
    response_model=ApiResponse[list[ContractResponse]],
    summary="获取合同审查历史",
)
def list_contracts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[list[ContractResponse]]:
    """返回当前用户的合同记录。"""
    contracts = list(
        db.scalars(
            select(Contract)
            .where(Contract.user_id == current_user.id)
            .order_by(Contract.created_at.desc(), Contract.id.desc())
        ).all()
    )
    return ApiResponse(data=contracts)
