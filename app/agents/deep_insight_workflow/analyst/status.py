from pydantic import BaseModel

class AnalystStatus(BaseModel):
    is_running: bool = False
    last_error: str = None
