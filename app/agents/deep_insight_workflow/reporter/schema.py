from pydantic import BaseModel
from typing import List, Optional

class ReporterInput(BaseModel):
    topic: str
    crawler_data: List[dict]
    urls: List[str]

class ReporterOutput(BaseModel):
    news_content: str
