from pydantic import BaseModel
from typing import Optional

class TranslatorInput(BaseModel):
    topic: str

class TranslatorOutput(BaseModel):
    english_query: Optional[str]
