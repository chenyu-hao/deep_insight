from typing import List, Optional, Dict, Any

from pydantic import BaseModel

class XHSPublisherInput(BaseModel):
    final_copy: str
    image_urls: List[str]
    topic: str
    xhs_publish_enabled: bool = False

class XHSPublisherOutput(BaseModel):
    xhs_publish_result: Optional[Dict[str, Any]]
