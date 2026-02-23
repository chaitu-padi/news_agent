from pydantic import BaseModel, Field
from typing import Optional

class NormalizedNews(BaseModel):
    id: str
    timestamp: str
    source_type: str 
    source_name: str
    headline: str
    content: str
    is_authorized: bool = False
