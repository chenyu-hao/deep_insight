from pydantic import BaseModel
from typing import List, Optional

class DebaterInput(BaseModel):
    initial_analysis: str
    topic: str
    news_content: str
    revision_count: int
    debate_rounds: int

class DebaterOutput(BaseModel):
    critique: str
    debate_history: List[str]
