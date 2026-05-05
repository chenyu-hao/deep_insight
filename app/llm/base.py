from typing import List, Optional, Dict
from app.core.config import settings

class KeyManager:
    def __init__(self, keys, provider_name="Unknown"):
        self.keys = [k for k in (keys or []) if k]
        self.provider_name = provider_name
        self._idx = 0

    def get_next_key(self):
        if not self.keys:
            raise ValueError(f"No API keys configured for {self.provider_name}.")
        k = self.keys[self._idx % len(self.keys)]
        self._idx = (self._idx + 1) % len(self.keys)
        return k

_key_managers: Dict[str, KeyManager] = {}

def get_manager(provider_key: str, keys: List[str], provider_name: str) -> KeyManager:
    """
    Keep per-provider rotation state while allowing keys to change at runtime.
    If keys changed, replace the manager.
    """
    pk = (provider_key or "").strip().lower()
    existing = _key_managers.get(pk)
    normalized = [k for k in (keys or []) if k]
    if not existing or existing.keys != normalized:
        existing = KeyManager(normalized, provider_name)
        _key_managers[pk] = existing
    return existing
