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

# --- 配置相关 Schema ---
class LLMProviderConfig(BaseModel):
    provider: str
    model: str

class AgentConfig(BaseModel):
    reporter: List[LLMProviderConfig]
    analyst: List[LLMProviderConfig]
    debater: List[LLMProviderConfig]
    writer: List[LLMProviderConfig]

class CrawlerLimit(BaseModel):
    max_items: int
    max_comments: int

class ConfigResponse(BaseModel):
    llm_providers: Dict[str, List[LLMProviderConfig]]
    crawler_limits: Dict[str, CrawlerLimit]
    debate_max_rounds: int
    default_platforms: List[str]

class ConfigUpdateRequest(BaseModel):
    debate_max_rounds: Optional[int] = None
    crawler_limits: Optional[Dict[str, CrawlerLimit]] = None
    default_platforms: Optional[List[str]] = None

# --- 输出文件相关 Schema ---
class OutputFileInfo(BaseModel):
    filename: str
    topic: str
    created_at: str
    size: int

class OutputFileListResponse(BaseModel):
    files: List[OutputFileInfo]
    total: int

class OutputFileContentResponse(BaseModel):
    filename: str
    content: str
    created_at: str

# --- 工作流状态相关 Schema ---
class WorkflowStatusResponse(BaseModel):
    running: bool
    current_step: Optional[str] = None
    progress: int = 0
    started_at: Optional[str] = None
    topic: Optional[str] = None
