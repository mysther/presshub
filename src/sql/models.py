from sqlalchemy import JSON, Column, DateTime, Integer, String

from .database import Base


class ArticleBase(Base):
    __tablename__ = "article"

    url = Column(String, primary_key=True, index=True)
    writen_timestamp = Column(DateTime)

class ArticleCreate(ArticleBase):
    pass

class Article(ArticleBase):
    id = Column(Integer, index=True)
    publisher = Column(String)
    name = Column(String, index=True)
    filename = Column(String)
    archived_path = Column(String, unique=True)
    saved_timestamp = Column(DateTime)

    
class WebsiteSession(Base):
    __tablename__ = "website_session"
    hostname = Column(String, primary_key=True, index=True)
    storage_state = Column(JSON)