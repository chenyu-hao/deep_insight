from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class NewsRequest(BaseModel):
    urls: List[str] = []
    topic: str
    platforms: Optional[List[str]] = None  # Optional: specify platforms to crawl

class AgentState(BaseModel):
    agent_name: str
    step_content: str
    status: str  # 'thinking' | 'finished' | 'error'

class CrawlerDataItem(BaseModel):
    """Standardized crawler data item"""
    platform: str
    content_id: str
    title: str
    content: str
    author: Dict[str, Any]
    interactions: Dict[str, Any]
    timestamp: str
    url: str
    raw_data: Dict[str, Any]
