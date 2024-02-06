from sqlalchemy import Column, DateTime, Integer, String

from .database import Base


class ArticleBase(Base):
    __tablename__ = "articles"

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