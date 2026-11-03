# 法宝 - AI法律助手 FastAPI 后端

这是项目的 Python 后端，采用 FastAPI、SQLAlchemy 2.0、Alembic、Pydantic V2 和 MySQL 5.7。AI 咨询、文书生成和合同审查目前使用可替换的模拟服务，后续可以在 `app/services/ai_service.py` 中接入 FastGPT。

## 环境要求

- Python 3.11 及以上（本机 Python 3.13 也可以）
- MySQL 5.7+，本项目默认连接 `127.0.0.1:3306`
- Windows PowerShell（以下命令均从 `backend` 目录执行）

## 安装

```powershell
cd "D:\法律智能体\法宝 - AI法律助手\backend"
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

编辑 `.env`，至少修改 `DATABASE_URL` 和 `JWT_SECRET_KEY`。JWT 密钥可以用下面的命令生成：

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

## 数据库初始化

Alembic 不会自动创建 MySQL 数据库，先在 MySQL 客户端执行：

```sql
CREATE DATABASE fabao DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

然后在 `backend` 目录执行迁移：

```powershell
alembic upgrade head
```

回滚最近一次迁移：

```powershell
alembic downgrade -1
```

## 启动

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Swagger 文档：`http://127.0.0.1:8000/docs`
- ReDoc 文档：`http://127.0.0.1:8000/redoc`
- 健康检查：`http://127.0.0.1:8000/health`

## API 概览

所有业务接口前缀为 `/api/v1`，成功和失败响应都采用 `{code, message, data}` 结构。HTTP 状态码表达协议状态，`code` 是对应的业务码。

- `/auth/register`、`/auth/login`、`/auth/me`：注册、登录和当前用户
- `/chat/conversations`：对话的增删查及消息收发
- `/documents/generate`、`/documents/list`、`/documents/{id}`：文书生成和历史记录
- `/contracts/upload`、`/contracts/review/{id}`、`/contracts/list`：合同上传、审查和历史记录

除注册和登录外的接口需要 `Authorization: Bearer <JWT>`。登录接口的 `username` 字段既可填写用户名，也可填写邮箱。

## 前端对接

现有 Vue/Vite 前端开发端口为 `5173`，后端 CORS 默认已放行 `localhost:5173` 和 `127.0.0.1:5173`。前端可以直接请求 `http://localhost:8000/api/v1`，也可以在 Vite 中配置 `/api` 代理。

合同只接受 `.docx` 和 `.pdf`，单文件上限为 10MB。文件使用随机名称保存到 `uploads/`，原始文件名仅保存到数据库；扫描版 PDF 没有文本层时需要额外 OCR，当前服务会返回友好提示。

