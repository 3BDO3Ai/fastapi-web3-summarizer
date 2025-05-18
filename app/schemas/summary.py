from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime

class SummarizeRequest(BaseModel):
    wallet_address: str
    signature: str
    article_url: HttpUrl

class SummaryResponse(BaseModel):
    id: int
    wallet_address: str
    article_url: str
    summary_content: str
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True

class SummaryListResponse(BaseModel):
    summaries: List[SummaryResponse]
