"""
✘ Доступные команды -

• `{i}gemini <запрос>`
    Получить ответ от Google Gemini.

• `{i}antr <запрос>`
    Получить ответ от Anthropic Claude.

• `{i}gpt <запрос>`
    Получить ответ от OpenAI GPT.

• `{i}deepseek <запрос>`
    Получить ответ от DeepSeek AI.

Установите пользовательские модели с помощью:
    • OPENAI_MODEL: по умолчанию: gpt-4o-mini
    • ANTHROPIC_MODEL: claude-3-opus-20240229
    • GEMINI_MODEL: gemini-1.5-flash
    • DEEPSEEK_MODEL: deepseek-chat
"""

import json
from . import LOGS, eor, get_string, udB, ultroid_cmd, async_searcher
import aiohttp
import asyncio


ENDPOINTS = {
    "gpt": "https://api.openai.com/v1/chat/completions",
    "antr": "https://api.anthropic.com/v1/messages",
    "gemini": "https://generativelanguage.googleapis.com/v1beta/chat/completions",
    "deepseek": "https://api.deepseek.com/chat/completions"
}

DEFAULT_MODELS = {
    "gpt": "gpt-4o-mini",
    "antr": "claude-3-opus-20240229",
    "gemini": "gemini-1.5-flash",
    "deepseek": "deepseek-chat"
}


def get_model(provider):
    """Получить имя модели из базы данных или использовать по умолчанию"""
    model_keys = {
        "gpt": "OPENAI_MODEL",
        "antr": "ANTHROPIC_MODEL",
        "gemini": "GEMINI_MODEL",
        "deepseek": "DEEPSEEK_MODEL"
    }
    return udB.get_key(model_keys[provider]) or DEFAULT_MODELS[provider]
