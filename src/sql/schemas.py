from datetime import datetime
from typing import TypedDict
from pydantic import BaseModel

class ArticleBase(BaseModel):
    url: str
    writen_timestamp: datetime

class ArticleCreate(ArticleBase):
    pass

class Article(ArticleBase):
    id: int
    name: str
    publisher: str
    filename: str
    archived_path: str
    saved_timestamp: datetime

    class Config:
        from_attributes = True

class WebsiteSession(BaseModel):
    hostname: str
    storage_state: TypedDict

    class Config:
        from_attributes = True