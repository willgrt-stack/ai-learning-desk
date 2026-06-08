"""
AI学习桌 - 对话引擎
核心：判断孩子意图 → 选教学策略 → 调 LLM → 返回结构化结果
"""

import json
from datetime import datetime
from llm import LLMClient


# ─── 系统提示词模板 ─────────────────────────────────────────────────

SYSTEM_PROMPT_TEMPLATE = """你是一个温和耐心的小学AI学习伙伴。你在辅导{child_name}。

## 教学原则
- 不直接给答案，用引导和提问的方式帮助孩子自己思考。
- {rules}
- AI 输出必须是 JSON 格式。

## 输出格式
你必须严格按照以下 JSON 格式输出，不要包含其他内容：

```json
{{
  "cards": [
    {{"type": "seen", "title": "我听到你说啦", "body": "复述孩子刚说的话，表示你听懂了"}},
    {{"type": "intent", "title": "我判断你是想", "body": "你判断的意图，比如：拍题讲解 / 聊天 / 练口语 / 复习错题"}},
    {{"type": "first_step", "title": "我们先…", "body": "给孩子的第一步引导或回应"}},
    {{"type": "hint", "title": "小提示", "body": "如果需要，给一个温和的提示"}},
    {{"type": "try", "title": "你试试看", "body": "让孩子动手或动脑的一步"}}
  ],
  "speak_text": "你要对孩子说的话，语气亲切自然",
  "badge": "给孩子的一个小称号，比如：审题小侦探 / 计算小能手 / 思考小达人",
  "next_step": "你期望孩子下一步做什么",
  "challenge": "同类变式题（如果需要），没有就写空字符串",
  "need_parent_review": false,
  "ai_confidence": "高"
}}
```

## 孩子的信息
{child_profile}
"""

CHILD_RULES = {
    "姐姐": "- 姐姐数学基础中等，重点是审题和过程，多追问「你是怎么想的」。",
    "童童": "- 童童还在低年级，一次只问一个问题，多用鼓励。",
}

CHILD_PROFILES = {
    "姐姐": "四年级，数学中等，需要加强审题和计算过程。",
    "童童": "二年级，刚开始接触数学，需要耐心引导和鼓励。",
}


# ─── 意图判断提示词 ───────────────────────────────────────────────

INTENT_PROMPT = """判断孩子当前想做什么。只输出一个词：
- homework: 问作业/讲题
- chat: 闲聊/聊天
- oral: 练口语/朗读
- review: 复习错题
- screen: 屏幕共享/看屏幕内容
- unknown: 不确定

孩子说：{input}
"""


# ─── 对话引擎 ──────────────────────────────────────────────────────

class ConversationEngine:
    """核心对话引擎"""

    def __init__(self, child_name: str = "姐姐"):
        self.child_name = child_name
        self.llm = LLMClient()

    def detect_intent(self, user_input: str) -> str:
        """判断孩子意图"""
        prompt = INTENT_PROMPT.format(input=user_input)
        resp = self.llm.chat([{"role": "user", "content": prompt}], temperature=0.3)
        if resp["error"]:
            return "unknown"
        intent = resp["content"].strip().lower()
        valid = {"homework", "chat", "oral", "review", "screen", "unknown"}
        return intent if intent in valid else "unknown"

    def respond(self, user_input: str, intent: str = None) -> dict:
        """
        处理孩子输入，返回教学响应
        user_input: 孩子的文字输入
        intent:     可选，如果不传则自动判断
        返回:       dict (包含 cards, speak_text, badge 等)
        """
        if intent is None:
            intent = self.detect_intent(user_input)

        rules = CHILD_RULES.get(self.child_name, "")
        profile = CHILD_PROFILES.get(self.child_name, "")

        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            child_name=self.child_name,
            rules=rules,
            child_profile=profile,
        )

        user_prompt = f"## 孩子当前意图\n{intent}\n\n## 孩子说的话\n{user_input}"

        resp = self.llm.chat_structured(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )

        if resp["error"]:
            return {
                "cards": [
                    {"type": "seen", "title": "嗯？", "body": "我没听清楚，能再说一遍吗？"},
                    {"type": "intent", "title": "判断结果", "body": f"自动判断为: {intent}"},
                ],
                "speak_text": "我没听清楚，能再说一遍吗？",
                "badge": "",
                "next_step": "等待孩子重新输入",
                "challenge": "",
                "need_parent_review": True,
                "ai_confidence": "低",
                "error": resp["error"],
                "is_mock": False,
                "used_provider": resp["provider"],
                "used_model": resp["model"],
                "latency_ms": resp["latency_ms"],
            }

        result = resp["content"]
        result["detected_intent"] = intent
        result["is_mock"] = False
        result["used_provider"] = resp["provider"]
        result["used_model"] = resp["model"]
        result["latency_ms"] = resp["latency_ms"]
        result["error"] = None
        return result


# ─── 快速测试 ──────────────────────────────────────────────────────

if __name__ == "__main__":
    engine = ConversationEngine("姐姐")
    result = engine.respond("我不会 12.5 减 3.8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
