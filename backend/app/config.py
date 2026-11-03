"""应用配置模块。

所有可变配置都从项目根目录下的 ``.env`` 读取，代码中只保留适合本地开发
的默认值。生产环境务必替换数据库密码和 JWT 密钥。
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """集中管理 FastAPI、数据库、认证和文件上传配置。"""

    app_name: str = "法宝 - AI法律助手"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"

    # MySQL 5.7 默认连接串；部署时请通过 .env 覆盖。
    database_url: str = (
        "mysql+pymysql://root:root@127.0.0.1:3306/fabao?charset=utf8mb4"
    )

    # JWT 配置。生产环境必须使用随机且足够长的密钥。
    jwt_secret_key: str = "please-change-this-secret-key-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    # CORS 支持逗号分隔的多个来源，也支持 JSON 数组形式。
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # 上传文件保存目录及单文件大小上限（10 MB）。
    upload_dir: str = "uploads"
    max_upload_size: int = 10 * 1024 * 1024

    # FastGPT 预留配置；当前默认使用模拟 AI 服务。
    fastgpt_base_url: str = "http://localhost:3000"
    fastgpt_api_key: str = ""
    fastgpt_app_id: str = ""
    # 可选：绑定固定会话实现多轮上下文；留空时每次请求为独立对话。
    fastgpt_chat_id: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """将环境变量中的 CORS 字符串转换为 FastAPI 可用的列表。"""
        value = self.cors_origins.strip()
        if value.startswith("["):
            try:
                import json

                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed if str(item).strip()]
            except (TypeError, ValueError):
                pass
        return [item.strip() for item in value.split(",") if item.strip()]

    @property
    def upload_path(self) -> Path:
        """返回上传目录的 Path 对象，目录创建由应用启动流程负责。"""
        return Path(self.upload_dir)


@lru_cache
def get_settings() -> Settings:
    """缓存配置对象，避免每次依赖注入都重复读取 .env。"""
    return Settings()


settings = get_settings()
