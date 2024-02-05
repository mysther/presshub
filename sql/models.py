from sqlalchemy import Column, DateTime, Integer, String

from .database import Base

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)
    website = Column(String)
    url = Column(String)
    saved_path = Column(String)
    saved_timestamp = Column(DateTime)
    writen_timestamp = Column(DateTime)