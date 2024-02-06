from typing import Union
from sqlalchemy import delete
from sqlalchemy.orm import Session
from urllib.parse import urlparse
from datetime import datetime
import os

from . import models, schemas
from config.config import get_settings

def get_article(db: Session, url: str):
    db_article = db.query(models.Article).filter(models.Article.url == url).first()

    if db_article and not os.path.exists(db_article.archived_path):
        delete_article(db, db_article.url)
        db_article = None

    return db_article

def delete_article(db: Session, url: str):
    stmt = delete(models.Article).where(models.Article.url == url).returning(models.Article.archived_path)
    deleted_article: Union[models.Article, None] = db.execute(stmt).fetchone()
    
    if os.path.exists(deleted_article.archived_path):
        os.remove(deleted_article.archived_path)

    return deleted_article

def get_articles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Article).offset(skip).limit(limit).all()

def save_article(db: Session, article: schemas.ArticleCreate):
    db_article = models.Article(**article.model_dump())
    
    parsed_url = urlparse(article.url)

    db_article.id = 0
    db_article.publisher = parsed_url.netloc.split(".")[-2]
    db_article.name = parsed_url.path.split("/")[-1]

    publisher_folder: str = os.path.join(get_settings().data_path, db_article.publisher)
    if not os.path.exists(publisher_folder):
        os.makedirs(publisher_folder)

    db_article.filename = db_article.name + ".pdf"
    db_article.archived_path = os.path.join(publisher_folder, db_article.filename)
    db_article.saved_timestamp=datetime.now()
    
    
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article