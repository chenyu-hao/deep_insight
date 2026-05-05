from typing import List, Optional, Dict, Any

from pydantic import BaseModel

class CrawlerInput(BaseModel):
    topic: str
    platforms: List[str]

class CrawlerOutput(BaseModel):
    crawler_data: List[Dict[str, Any]]
    platform_data: Dict[str, List[Dict[str, Any]]]
