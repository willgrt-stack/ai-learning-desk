"""
AI学习桌 - 多模型 LLM 客户端
支持：豆包 / DeepSeek，统一接口，可扩展
"""

import json
import time
from openai import OpenAI
from config import LLMConfig


class LLMClient:
    """统一的 LLM 调用接口"""

    def __init__(self, provider: str = None):
        cfg = LLMConfig.get_active()
        if provider:
            cfg["provider"] = provider
            cfg.update(LLMConfig.get_active())

        self.provider = cfg["provider"]
        self.model = cfg["model"]
        self.client = OpenAI(
            api_key=cfg["api_key"],
            base_url=cfg["base_url"],
        )

    def chat(self, messages: list, temperature: float = 0.7) -> dict:
        """
        调用 LLM 进行对话
        messages: [{"role": "system"|"user"|"assistant", "content": "..."}]
        返回: {"content": "...", "model": "...", "latency_ms": ..., "provider": "..."}
        """
        start = time.time()
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
            )
            elapsed = int((time.time() - start) * 1000)
            return {
                "content": resp.choices[0].message.content,
                "model": resp.model,
                "latency_ms": elapsed,
                "provider": self.provider,
                "error": None,
            }
        except Exception as e:
            elapsed = int((time.time() - start) * 1000)
            return {
                "content": None,
                "model": self.model,
                "latency_ms": elapsed,
                "provider": self.provider,
                "error": str(e),
            }

    def chat_structured(self, messages: list, response_format: dict, temperature: float = 0.7) -> dict:
        """
        结构化输出调用（JSON mode）
        response_format: {"type": "json_object"}
        """
        start = time.time()
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format=response_format,
                temperature=temperature,
            )
            elapsed = int((time.time() - start) * 1000)
            content = resp.choices[0].message.content
            return {
                "content": json.loads(content) if content else None,
                "model": resp.model,
                "latency_ms": elapsed,
                "provider": self.provider,
                "error": None,
            }
        except Exception as e:
            elapsed = int((time.time() - start) * 1000)
            return {
                "content": None,
                "model": self.model,
                "latency_ms": elapsed,
                "provider": self.provider,
                "error": str(e),
            }

    def is_available(self) -> bool:
        """快速检查 LLM 是否可用"""
        try:
            self.client.models.list()
            return True
        except Exception:
            return False
