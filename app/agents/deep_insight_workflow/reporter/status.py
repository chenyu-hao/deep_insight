from pydantic import BaseModel

class ReporterStatus(BaseModel):
    is_running: bool = False
    last_error: str = None
