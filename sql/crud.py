from sqlalchemy.orm import Session

from . import models, schemas

def get_article(db: Session, website: str, name: str):
    return db.query(models.Article).filter(models.Article.website == website, models.Article.name == name).first()

def get_articles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Article).offset(skip).limit(limit).all()

def save_article(db: Session, article: schemas.Article):
    db_article = models.Article(**article.model_dump())
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article