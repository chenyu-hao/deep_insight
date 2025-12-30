from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from app.config import settings
import os
from itertools import cycle

class KeyManager:
    def __init__(self, keys):
        self.keys = [k for k in keys if k]
        self.key_cycle = cycle(self.keys) if self.keys else None

    def get_next_key(self):
        if not self.key_cycle:
            raise ValueError("No API keys configured for this provider.")
        return next(self.key_cycle)

# Initialize key managers
gemini_key_manager = KeyManager(settings.GEMINI_API_KEYS)
moonshot_key_manager = KeyManager(settings.MOONSHOT_API_KEYS)
deepseek_key_manager = KeyManager(settings.DEEPSEEK_API_KEYS)
doubao_key_manager = KeyManager(settings.DOUBAO_API_KEYS)
zhipu_key_manager = KeyManager(settings.ZHIPU_API_KEYS)

def get_llm(provider: str, model_name: str):
    """
    Factory function to get an LLM instance based on provider and model.
    """
    if provider == "google" or provider == "gemini":
        # Rotate API Key
        current_key = gemini_key_manager.get_next_key()
        
        print(f"[INFO] Using Gemini Key: ...{current_key[-6:]}")
        
        return ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0.7,
            google_api_key=current_key,
            convert_system_message_to_human=True
        )
        
    elif provider == "moonshot":
        current_key = moonshot_key_manager.get_next_key()
        print(f"[INFO] Using Moonshot Key: ...{current_key[-6:]}")
        return ChatOpenAI(
            model=model_name,
            temperature=0.7,
            api_key=current_key,
            base_url=settings.MOONSHOT_BASE_URL
        )

    elif provider == "openai":
        return ChatOpenAI(
            model=model_name,
            temperature=0.7,
            api_key=settings.OPENAI_API_KEY
        )

    elif provider == "deepseek":
        current_key = deepseek_key_manager.get_next_key()
        print(f"[INFO] Using DeepSeek Key: ...{current_key[-6:]}")
        return ChatOpenAI(
            model=model_name,
            temperature=0.7,
            api_key=current_key,
            base_url=settings.DEEPSEEK_BASE_URL
        )

    elif provider == "doubao":
        current_key = doubao_key_manager.get_next_key()
        print(f"[INFO] Using Doubao Key: ...{current_key[-6:]}")
        return ChatOpenAI(
            model=model_name,
            temperature=0.7,
            api_key=current_key,
            base_url=settings.DOUBAO_BASE_URL
        )

    elif provider == "zhipu":
        current_key = zhipu_key_manager.get_next_key()
        print(f"[INFO] Using Zhipu Key: ...{current_key[-6:]}")
        return ChatOpenAI(
            model=model_name,
            temperature=0.7,
            api_key=current_key,
            base_url=settings.ZHIPU_BASE_URL
        )
    
    else:
        raise ValueError(f"Unsupported LLM Provider: {provider}")

def get_agent_llm(agent_name: str):
    """
    Get a specific LLM instance for a named agent based on AGENT_CONFIG.
    """
    config = settings.AGENT_CONFIG.get(agent_name)
    if not config:
        # Fallback to default if agent not found
        return get_llm("gemini", settings.GEMINI_MODEL)
    
    return get_llm(config["provider"], config["model"])
