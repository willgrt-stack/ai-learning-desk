"""
AI学习桌 - 配置管理
从 .env 加载 API 密钥和模型配置
"""

import os
from dotenv import load_dotenv

load_dotenv()


class LLMConfig:
    """大语言模型配置"""
    
    # 当前使用的 LLM 提供商
    provider = os.getenv("LLM_PROVIDER", "doubao")
    
    # ---- 豆包 (火山引擎) ----
    doubao_api_key = os.getenv("DOUBAO_API_KEY", "")
    doubao_model = os.getenv("DOUBAO_MODEL", "doubao-pro-32k")
    doubao_base_url = os.getenv("DOUBAO_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
    
    # ---- DeepSeek ----
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY", "")
    deepseek_model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    
    @classmethod
    def get_active(cls):
        """获取当前激活的 LLM 配置"""
        if cls.provider == "doubao":
            return {
                "api_key": cls.doubao_api_key,
                "model": cls.doubao_model,
                "base_url": cls.doubao_base_url,
                "provider": "doubao",
            }
        elif cls.provider == "deepseek":
            return {
                "api_key": cls.deepseek_api_key,
                "model": cls.deepseek_model,
                "base_url": "https://api.deepseek.com",
                "provider": "deepseek",
            }
        else:
            raise ValueError(f"不支持的 LLM 提供商: {cls.provider}")


class TTSConfig:
    """语音合成配置 (豆包)"""
    
    app_id = os.getenv("DOUBAO_TTS_APP_ID", "")
    access_token = os.getenv("DOUBAO_TTS_ACCESS_TOKEN", "")
    voice = os.getenv("DOUBAO_TTS_VOICE", "zh_female_anqi")
    
    @classmethod
    def is_ready(cls):
        return bool(cls.app_id and cls.access_token)


class AppConfig:
    """应用全局配置"""
    
    data_dir = os.getenv("DATA_DIR", "/Users/willgrt/Documents/AI学习桌")
    debug = os.getenv("DEBUG", "true").lower() == "true"
    
    # 各孩子的学习画像路径
    children = {
        "姐姐": {
            "profile": f"{data_dir}/01_姐姐/00_学习画像.md",
            "daily_dir": f"{data_dir}/01_姐姐/01_每日记录/",
        },
        "童童": {
            "profile": f"{data_dir}/02_童童/00_学习画像.md",
            "daily_dir": f"{data_dir}/02_童童/01_每日记录/",
        },
    }
