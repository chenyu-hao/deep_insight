from pydantic import BaseModel

class TranslatorStatus(BaseModel):
    is_running: bool = False
    last_error: str = None
