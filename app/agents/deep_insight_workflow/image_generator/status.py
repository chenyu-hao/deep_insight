from pydantic import BaseModel

class ImageGeneratorStatus(BaseModel):
    is_running: bool = False
    last_error: str = None
