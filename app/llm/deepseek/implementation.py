from langchain_openai import ChatOpenAI
from typing import Optional, List
from app.core.config import settings
from app.llm.base import get_manager

def get_deepseek_llm(model_name: str, api_key: Optional[str] = None, effective_keys: Optional[List[str]] = None):
    if api_key:
        current_key = api_key
        print(f"🔑 Using Agent-specific DeepSeek Key: ...{current_key[-6:]}")
    else:
        keys = effective_keys if effective_keys is not None else settings.DEEPSEEK_API_KEYS
        current_key = get_manager("deepseek", keys, "DeepSeek").get_next_key()
        print(f"🔑 Using DeepSeek Key: ...{current_key[-6:]}")
    return ChatOpenAI(
        model=model_name,
        temperature=0.7,
        api_key=current_key,
        base_url=settings.DEEPSEEK_BASE_URL
    )
