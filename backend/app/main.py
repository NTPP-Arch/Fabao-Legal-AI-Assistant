"""FastAPI 应用入口：中间件、路由和全局异常处理。"""

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api import auth, chat, contract, document
from app.config import settings
from app.core.exceptions import AppException


@asynccontextmanager
async def lifespan(_: FastAPI):
    """应用生命周期：启动时确保上传目录存在。"""
    settings.upload_path.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title=settings.app_name,
    description="法宝 AI 法律助手后端 API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppException)
async def app_exception_handler(_: Request, exc: AppException) -> JSONResponse:
    """将业务异常转换为统一响应结构。"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.code, "message": exc.message, "data": exc.data},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    """统一处理 FastAPI/认证组件产生的 HTTPException。"""
    detail = exc.detail
    message = detail if isinstance(detail, str) else "请求失败"
    data: Any = None if isinstance(detail, str) else detail
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "message": message, "data": data},
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    """统一处理 Pydantic V2 参数校验错误。"""
    return JSONResponse(
        status_code=422,
        # jsonable_encoder 可将 Pydantic 错误上下文中的 ValueError 转成字符串。
        content={"code": 422, "message": "请求参数校验失败", "data": jsonable_encoder(exc.errors())},
    )


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(_: Request, exc: SQLAlchemyError) -> JSONResponse:
    """避免数据库异常泄露 SQL 细节，并返回统一错误结构。"""
    # 详细异常只应写入服务端日志；这里不向客户端暴露连接串或 SQL。
    _ = exc
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "数据库操作失败", "data": None},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    """兜底处理未预期异常，生产环境不返回堆栈信息。"""
    _ = exc
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "服务器内部错误", "data": None},
    )


@app.get("/", tags=["系统"], summary="服务信息")
def root() -> dict[str, object]:
    """返回服务名称和 API 前缀，便于快速检查服务是否启动。"""
    return {
        "code": 200,
        "message": "success",
        "data": {"name": settings.app_name, "api_prefix": settings.api_v1_prefix},
    }


@app.get("/health", tags=["系统"], summary="健康检查")
def health() -> dict[str, object]:
    """轻量健康检查，不主动建立数据库连接。"""
    return {"code": 200, "message": "success", "data": {"status": "ok"}}


app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(chat.router, prefix=settings.api_v1_prefix)
app.include_router(document.router, prefix=settings.api_v1_prefix)
app.include_router(contract.router, prefix=settings.api_v1_prefix)
