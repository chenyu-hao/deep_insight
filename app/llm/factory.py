from typing import Optional, List, Dict
from app.core.config import settings
from app.services.settings.user_settings import get_agent_llm_overrides, get_agent_api_config, get_effective_llm_keys

_PROVIDER_KEY_MAP = {
    "gemini": ("gemini", "Gemini", lambda: settings.GEMINI_API_KEYS),
    "google": ("gemini", "Gemini", lambda: settings.GEMINI_API_KEYS),
    "moonshot": ("kimi", "Moonshot", lambda: settings.MOONSHOT_API_KEYS),
    "openai": ("openai", "OpenAI", lambda: [settings.OPENAI_API_KEY] if settings.OPENAI_API_KEY else []),
    "deepseek": ("deepseek", "DeepSeek", lambda: settings.DEEPSEEK_API_KEYS),
    "doubao": ("doubao", "Doubao", lambda: settings.DOUBAO_API_KEYS),
    "zhipu": ("zhipu", "Zhipu", lambda: settings.ZHIPU_API_KEYS),
    "minimax": ("minimax", "MiniMax", lambda: settings.MINIMAX_API_KEYS),
}

def _resolve_effective_keys(provider: str) -> Optional[List[str]]:
    info = _PROVIDER_KEY_MAP.get(provider.lower())
    if not info:
        return None
    provider_key, _display_name, env_keys_fn = info
    return get_effective_llm_keys(provider_key=provider_key, env_keys=env_keys_fn())


# Import implementations
from app.llm.gemini.implementation import get_gemini_llm
from app.llm.openai.implementation import get_openai_llm
from app.llm.moonshot.implementation import get_moonshot_llm
from app.llm.deepseek.implementation import get_deepseek_llm
from app.llm.doubao.implementation import get_doubao_llm
from app.llm.zhipu.implementation import get_zhipu_llm
from app.llm.minimax.implementation import get_minimax_llm

def get_llm(provider: str, model_name: str, api_key: Optional[str] = None):
    """
    Factory function to get an LLM instance based on provider and model.
    """
    p = provider.lower()
    effective_keys = _resolve_effective_keys(p)
    
    if p in ["google", "gemini"]:
        return get_gemini_llm(model_name, api_key, effective_keys)
    elif p == "moonshot":
        return get_moonshot_llm(model_name, api_key, effective_keys)
    elif p == "openai":
        return get_openai_llm(model_name, api_key, effective_keys)
    elif p == "deepseek":
        return get_deepseek_llm(model_name, api_key, effective_keys)
    elif p == "doubao":
        return get_doubao_llm(model_name, api_key, effective_keys)
    elif p == "zhipu":
        return get_zhipu_llm(model_name, api_key, effective_keys)
    elif p == "minimax":
        return get_minimax_llm(model_name, api_key, effective_keys)
    else:
        raise ValueError(f"Unsupported provider: {provider}")

def get_agent_llm(agent_role: str):
    """
    Get LLM for a specific agent role with fallback support.
    """
    configs = settings.AGENT_CONFIG.get(agent_role, [])

    # 1. Check for User Overrides (Runtime)
    overrides = get_agent_llm_overrides()
    override_data = overrides.get(agent_role)
    if override_data:
        provider = override_data.get("provider", "")
        model = override_data.get("model", "") or configs[0].get("model", "") if configs else ""
        api_config = get_agent_api_config(agent_role)
        api_key = api_config.get("api_key") if api_config else None
        
        if provider:
            try:
                return get_llm(provider, model, api_key=api_key)
            except Exception as e:
                print(f"⚠️ User override failed for {agent_role}: {e}. Falling back to default config.")

    # 2. Fallback to settings.AGENT_CONFIG
    for cfg in configs:
        try:
            return get_llm(cfg["provider"], cfg["model"])
        except Exception as e:
            print(f"⚠️ Provider {cfg['provider']} failed for {agent_role}: {e}. Trying next...")
    
    raise ValueError(f"All configured providers failed for agent: {agent_role}")
