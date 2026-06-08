"""
AI学习桌 - API 服务
FastAPI 后端，提供 LLM 对话 + TTS 语音合成接口
"""

import os
import json
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from conversation import ConversationEngine
from llm import LLMClient
from tts import TTSClient
from config import AppConfig

app = FastAPI(title="AI学习桌", version="0.1.0")

# 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 按孩子缓存对话引擎（后续可以加更多状态）
engines: dict[str, ConversationEngine] = {}


def get_engine(child: str) -> ConversationEngine:
    if child not in engines:
        engines[child] = ConversationEngine(child)
    return engines[child]


# ─── 请求/响应模型 ─────────────────────────────────────────────────

class ChatRequest(BaseModel):
    child: str = "姐姐"
    input: str
    intent: str = None  # 可选，不传则自动判断

class ChatResponse(BaseModel):
    cards: list
    speak_text: str
    badge: str
    next_step: str
    challenge: str
    need_parent_review: bool
    ai_confidence: str
    detected_intent: str
    is_mock: bool
    used_provider: str
    used_model: str
    latency_ms: int
    error: str = None

class TTSRequest(BaseModel):
    text: str
    voice: str = None

class TTSResponse(BaseModel):
    audio_base64: str = None
    format: str = None
    error: str = None


# ─── API 端点 ─────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"app": "AI学习桌", "version": "0.1.0", "status": "running"}

@app.get("/health")
def health():
    """健康检查"""
    return {"status": "ok", "time": datetime.now().isoformat()}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """
    核心对话接口
    孩子说话/拍题/看屏幕 → 返回教学引导
    """
    if req.child not in AppConfig.children:
        raise HTTPException(status_code=400, detail=f"未知的孩子: {req.child}，可选: {list(AppConfig.children.keys())}")

    engine = get_engine(req.child)
    result = engine.respond(req.input, intent=req.intent)
    return ChatResponse(**result)

@app.post("/tts", response_model=TTSResponse)
def tts(req: TTSRequest):
    """
    文字转语音 (豆包)
    把 AI 的回答转成自然语音
    """
    client = TTSClient()
    result = client.synthesize(req.text, voice=req.voice)
    return TTSResponse(**result)


# ─── 启动 ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8765"))
    print(f"🚀 AI学习桌 后端启动 → http://localhost:{port}")
    print(f"   API 文档 → http://localhost:{port}/docs")
    uvicorn.run(app, host="0.0.0.0", port=port)
