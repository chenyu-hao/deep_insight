from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class WriterInput(BaseModel):
    analysis: str
    topic: str
    news_content: str
    platform_data: Dict[str, List[Dict[str, Any]]]

class WriterOutput(BaseModel):
    final_copy: str
    output_file: Optional[str]
