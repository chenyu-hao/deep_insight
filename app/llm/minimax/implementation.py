from langchain_openai import ChatOpenAI
from typing import Optional, List
from app.core.config import settings
from app.llm.base import get_manager

def get_minimax_llm(model_name: str, api_key: Optional[str] = None, effective_keys: Optional[List[str]] = None):
    if api_key:
        current_key = api_key
        print(f"🔑 Using Agent-specific MiniMax Key: ...{current_key[-6:]}")
    else:
        keys = effective_keys if effective_keys is not None else settings.MINIMAX_API_KEYS
        current_key = get_manager("minimax", keys, "MiniMax").get_next_key()
        print(f"🔑 Using MiniMax Key: ...{current_key[-6:]}")
    return ChatOpenAI(
        model=model_name,
        temperature=0.7,
        api_key=current_key,
        base_url=settings.MINIMAX_BASE_URL
    )
