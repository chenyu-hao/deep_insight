from pydantic import BaseModel

class CrawlerStatus(BaseModel):
    is_running: bool = False
    current_platform: Optional[str] = None
    last_error: str = None
