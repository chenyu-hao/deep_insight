from pydantic import BaseModel

class XHSPublisherStatus(BaseModel):
    is_running: bool = False
    last_error: str = None
