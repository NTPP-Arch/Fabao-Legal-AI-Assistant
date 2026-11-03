"""AI 调用抽象层。

通过适配器隔离路由与具体模型供应商：``.env`` 中配置 ``FASTGPT_API_KEY`` 后
自动切换为 :class:`FastGPTClient` 对接项目中的 FastGPT 服务；
未配置时回退到 :class:`MockAIClient`，便于无密钥环境开发调试。
"""

import re
from dataclasses import dataclass, field

import httpx

from app.config import settings

_CITE_PATTERN = re.compile(r"\[CITE\s*\d+\]")


def strip_cite_markers(text: str) -> str:
    """去掉知识库引用标记（如 ``[CITE 39]``），让回复文本适合直接展示。"""
    return _CITE_PATTERN.sub("", text)


@dataclass
class MockAIClient:
    """开发阶段的确定性模拟客户端。"""

    def generate_reply(self, message: str, chat_id: str | None = None) -> str:
        """返回不调用外部服务的演示回复。"""
        return (
            "【模拟法律助手回复】已收到您的问题："
            f"{message}\n\n"
            "这是开发阶段的演示回复，具体法律意见请结合完整事实并咨询执业律师。"
        )


@dataclass
class FastGPTClient:
    """通过 FastGPT OpenAI 兼容接口调用真实 AI 服务。

    FastGPT 接口：``POST /api/v1/chat/completions``
    - 认证：``Authorization: Bearer <API Key>``（密钥在账号 → API 密钥 创建）
    - ``detail=False`` 只返回最终回答，不返回工作流中间过程
    - ``chatId`` 为空时每次请求是独立新对话；传入会话 ID 可实现多轮上下文
    """

    base_url: str = field(default_factory=lambda: settings.fastgpt_base_url)
    api_key: str = field(default_factory=lambda: settings.fastgpt_api_key)
    app_id: str = field(default_factory=lambda: settings.fastgpt_app_id)
    chat_id: str = field(default_factory=lambda: settings.fastgpt_chat_id)

    def generate_reply(self, message: str, chat_id: str | None = None) -> str:
        """调用 FastGPT 并返回最终回复文本。

        参数 ``chat_id`` 优先于配置中的默认会话：传入后 FastGPT 按该会话
        维护多轮上下文，后续请求复用同一 ``chat_id`` 即可追问。
        """
        url = f"{self.base_url.rstrip('/')}/api/v1/chat/completions"
        payload: dict[str, object] = {
            "stream": False,
            "detail": False,
            "messages": [{"role": "user", "content": message}],
        }
        if self.app_id:
            payload["appId"] = self.app_id
        if chat_id or self.chat_id:
            payload["chatId"] = chat_id or self.chat_id

        response = httpx.post(
            url,
            json=payload,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=120,
        )
        if response.status_code != 200:
            raise RuntimeError(
                f"FastGPT 调用失败（HTTP {response.status_code}）：{response.text[:300]}"
            )
        data = response.json()
        try:
            return str(data["choices"][0]["message"]["content"])
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"FastGPT 响应格式异常：{str(data)[:300]}") from exc


# 配置了 API Key 就走真实 FastGPT，否则回退到模拟客户端。
if settings.fastgpt_api_key:
    ai_client = FastGPTClient()
else:
    ai_client = MockAIClient()


def generate_legal_reply(message: str, chat_id: str | None = None) -> str:
    """通过当前 AI 适配器生成法律咨询回复（含去除引用标记）。"""
    return strip_cite_markers(ai_client.generate_reply(message, chat_id=chat_id))
