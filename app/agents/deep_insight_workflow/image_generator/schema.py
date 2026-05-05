from typing import List, Optional

from pydantic import BaseModel

class ImageGeneratorInput(BaseModel):
    final_copy: str
    initial_analysis: str
    image_count: int = 2

class ImageGeneratorOutput(BaseModel):
    image_urls: List[str]
