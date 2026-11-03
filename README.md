# 法宝 · 面向法律咨询场景的 RAG 与大模型应用

一个可运行的法律智能助手：**智能问答**、**合同审查**、**法律文书生成** 三大功能。
前端 Vue3 + Element Plus，后端 FastAPI + SQLAlchemy + MySQL，知识库与生成侧通过
FastGPT（OpenAI 兼容接口）接入，后端用适配器隔离了模型供应商，无密钥时可退回本地模拟。

> 仓库只包含源码与迁移脚本。**知识库语料、示例合同、`.env` 中的真实密钥都不在仓库里**，
> 见文末「不包含什么」。

## 三个功能

| 功能 | 入口 | 做了什么 |
|---|---|---|
| 智能问答 | `src/views/AiConsult.vue` → `POST /api/v1/chat` | 问题分类后走法律咨询链路，检索知识库并生成回答；回复里的 `[CITE n]` 引用标记在返回前统一剥离，避免前端直接显示检索编号 |
| 合同审查 | `src/views/ContractReview.vue` → `POST /api/v1/contract/review` | 上传合同 → 抽取条款 → 模型输出风险项 JSON → 后端归一化并用 **15 / 8 / 3** 权重（高/中/低）重算风险分（上限 100），不采信模型自报分值 |
| 文书生成 | `src/views/DocGenerate.vue` → `POST /api/v1/document/generate` | 按案由与要素拼提示词，生成起诉状 / 答辩状 / 律师函草稿 |

## 结构

```
├─ src/                     前端（Vue3）
│  ├─ api/                  axios 封装：http / auth / chat / contract / document
│  ├─ router/  stores/  components/
│  └─ views/                HomePage / AuthView / AiConsult / ContractReview / DocGenerate
├─ backend/                 后端（FastAPI）
│  ├─ app/
│  │  ├─ api/               auth / chat / contract / document 四个路由
│  │  ├─ models/            user / conversation / message / contract / document（5 张表）
│  │  ├─ schemas/           请求与响应模型
│  │  ├─ services/          ai_service（适配器）/ contract_service（风险分）/ document_service
│  │  ├─ core/              security（JWT）/ dependencies / exceptions
│  │  └─ utils/             file_handler（上传校验）
│  ├─ alembic/              迁移脚本（0001_initial_schema）
│  └─ requirements.txt
├─ index.html  vite.config.js  package.json
```

## 关键实现点

**1. AI 调用是可替换的适配器**
`backend/app/services/ai_service.py` 里 `FastGPTClient` 走 `POST /api/v1/chat/completions`，
`detail=False` 只取最终回答；`chat_id` 为空时每次请求是独立对话，传入会话 ID 就复用同一
多轮上下文。没有配置 `FASTGPT_API_KEY` 时自动回退到 `MockAIClient`，方便无密钥跑通全流程。

**2. 模型输出不可信，所以后端要重算**
- 引用：`strip_cite_markers()` 用正则清掉 `[CITE 39]` 这类标记。
- 合同风险：`_extract_json()` 先剥 ```` ```json ```` 围栏、再截取首尾大括号之间的内容；
  `_recompute_score()` 用 15/8/3 权重按风险条数重算总分并封顶 100 —— 保证分数与条数自洽。

**3. 认证与上传**
JWT（`core/security.py`）+ 依赖注入取当前用户（`core/dependencies.py`）；上传走
`utils/file_handler.py`，限制单文件 10 MB、落盘到 `uploads/`（该目录不进仓库）。

## 快速开始

后端（Python 3.10+）：

```bash
cd backend
python -m venv .venv && .venv\Scripts\activate      # Windows
pip install -r requirements.txt
copy .env.example .env                              # 然后填上自己的 FASTGPT_API_KEY 等
alembic upgrade head                                # 建表
uvicorn app.main:app --reload --port 8000
```

前端（Node 18+）：

```bash
npm install
npm run dev        # 默认 http://localhost:5173
npm run build      # 产物在 dist/
```

## 配置项

全部从 `backend/.env` 读取（`app/config.py` 里只有适合本地调试的默认值）：

| 变量 | 说明 |
|---|---|
| `DATABASE_URL` | 形如 `mysql+pymysql://user:pass@host:3306/db?charset=utf8mb4` |
| `JWT_SECRET_KEY` / `ACCESS_TOKEN_EXPIRE_MINUTES` | 登录态；生产务必换成随机长串 |
| `CORS_ORIGINS` | 逗号分隔或 JSON 数组，默认放行 Vite 的 5173 |
| `UPLOAD_DIR` / `MAX_UPLOAD_SIZE` | 上传落盘目录与大小上限 |
| `FASTGPT_BASE_URL` / `FASTGPT_API_KEY` / `FASTGPT_APP_ID` / `FASTGPT_CHAT_ID` | 知识库与工作流接入；留空则用模拟客户端 |

## 不包含什么

- **知识库语料与向量索引**：民法典、公司法、劳动合同法等全文与常见问答、指导性案例、
  合同审查要点是在 FastGPT 侧切分入库的（开发期共 9 个知识库、190 条知识条目），不在本仓库。
- **真实密钥**：只提供 `.env.example`，`.env` 已被 `.gitignore` 排除。
- **示例合同与上传件**：`backend/uploads/` 与 `dist/` 均排除。
- **依赖产物**：`node_modules/`、`backend/.venv/`、`__pycache__/`。

## 说明

课程 / 个人作品性质的项目，用于展示 RAG 知识库问答、结构化输出的后端归一化与前后端分离的
工程实现。法律意见仅供参考，不构成正式法律咨询。未附带开源许可证，如需复用请先联系作者。
