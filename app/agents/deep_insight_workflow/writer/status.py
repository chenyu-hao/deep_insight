from pydantic import BaseModel

class WriterStatus(BaseModel):
    is_running: bool = False
    last_error: str = None
