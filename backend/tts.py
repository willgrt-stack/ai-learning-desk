"""
AI学习桌 - 豆包语音合成 (TTS)
通过火山引擎接口，把文字转成自然语音
"""

import json
import base64
import httpx
from config import TTSConfig


class TTSClient:
    """豆包语音合成客户端"""

    def __init__(self):
        self.app_id = TTSConfig.app_id
        self.access_token = TTSConfig.access_token
        self.voice = TTSConfig.voice
        self.url = "https://openspeech.bytedance.com/api/v1/tts"

    def synthesize(self, text: str, voice: str = None) -> dict:
        """
        文字转语音
        text:   要朗读的文字
        voice:  音色 (默认用 .env 配置的)
        返回:   {"audio_base64": "...", "format": "mp3", "error": None}
        """
        if not TTSConfig.is_ready():
            return {"audio_base64": None, "format": None, "error": "TTS 未配置，请设置 DOUBAO_TTS_APP_ID 和 DOUBAO_TTS_ACCESS_TOKEN"}

        voice = voice or self.voice
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "app": {
                "appid": self.app_id,
                "token": self.access_token,
                "cluster": "volcano_tts",
            },
            "user": {
                "uid": "ai_learning_desk",
            },
            "audio": {
                "voice_type": voice,
                "encoding": "mp3",
                "speed_ratio": 1.0,
                "volume_ratio": 1.0,
                "pitch_ratio": 1.0,
            },
            "request": {
                "reqid": "",
                "text": text,
                "text_type": "plain",
                "operation": "query",
            },
        }

        try:
            resp = httpx.post(self.url, headers=headers, json=payload, timeout=30)
            if resp.status_code != 200:
                return {"audio_base64": None, "format": None, "error": f"TTS 请求失败: HTTP {resp.status_code}"}

            result = resp.json()
            if result.get("code") != 3000:
                return {"audio_base64": None, "format": None, "error": f"TTS 业务失败: code={result.get('code')}"}

            audio_b64 = result.get("data")
            return {"audio_base64": audio_b64, "format": "mp3", "error": None}

        except Exception as e:
            return {"audio_base64": None, "format": None, "error": f"TTS 异常: {str(e)}"}

    def is_ready(self) -> bool:
        return TTSConfig.is_ready()
