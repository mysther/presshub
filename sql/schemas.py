from datetime import datetime
from pydantic import BaseModel

class Article(BaseModel):
    id: int
    name: str
    url: str
    website: str
    saved_path: str
    saved_timestamp: datetime
    writen_timestamp: datetime

    class Config:
        orm_mode = True
