from langchain_openai import ChatOpenAI
from typing import Optional, List
from app.core.config import settings

def get_openai_llm(model_name: str, api_key: Optional[str] = None, effective_keys: Optional[List[str]] = None):
    if api_key:
        current_key = api_key
        print(f"🔑 Using Agent-specific OpenAI Key: ...{current_key[-6:]}")
    else:
        keys = effective_keys if effective_keys is not None else [settings.OPENAI_API_KEY]
        current_key = keys[0] if keys else settings.OPENAI_API_KEY
        print(f"🔑 Using OpenAI Key: ...{current_key[-6:]}")
    return ChatOpenAI(
        model=model_name,
        temperature=0.7,
        api_key=current_key
    )
