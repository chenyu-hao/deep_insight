from pydantic import BaseModel

class DebaterStatus(BaseModel):
    is_running: bool = False
    last_error: str = None
