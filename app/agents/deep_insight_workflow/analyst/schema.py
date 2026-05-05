from pydantic import BaseModel
from typing import List, Optional

class AnalystInput(BaseModel):
    news_content: str
    critique: Optional[str] = None
    revision_count: int = 0

class AnalystOutput(BaseModel):
    initial_analysis: str
    revision_count: int
    debate_history: List[str]
