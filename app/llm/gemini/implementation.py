from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Optional, List
from app.core.config import settings
from app.llm.base import get_manager

def get_gemini_llm(model_name: str, api_key: Optional[str] = None, effective_keys: Optional[List[str]] = None):
    if api_key:
        current_key = api_key
        print(f"🔑 Using Agent-specific Gemini Key: ...{current_key[-6:]}")
    else:
        keys = effective_keys if effective_keys is not None else settings.GEMINI_API_KEYS
        current_key = get_manager("gemini", keys, "Gemini").get_next_key()
        print(f"🔑 Using Gemini Key: ...{current_key[-6:]}")
    
    return ChatGoogleGenerativeAI(
        model=model_name,
        temperature=0.7,
        google_api_key=current_key,
        convert_system_message_to_human=True
    )
