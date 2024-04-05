from fastapi import FastAPI, HTTPException, Response, Depends
from fastapi.responses import JSONResponse
from playwright.async_api import async_playwright
from sqlalchemy.orm import Session

from typing import Union, Annotated
from urllib.parse import urlparse

from config.config import Settings, get_settings
from scraper.base_scraper import Scraper
from sql import crud, models, schemas
from sql.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/articles/", response_model=list[schemas.Article])
def read_articles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    articles = crud.get_articles(db, skip=skip, limit=limit)
    return articles

@app.get("/{url:path}")
async def catch_all(settings: Annotated[Settings, Depends(get_settings)], db: Session = Depends(get_db), url: Union[str, None] = None, download: Union[int, None] = None):
    
    parsed_url = urlparse(url)
    if not parsed_url.scheme and not parsed_url.netloc:
        return JSONResponse(status_code=200, content={"detail": "Service working. Please, add an Mediapart URL in the path."})
    elif not parsed_url.scheme == "https":
        raise HTTPException(status_code=400, detail="We only support https:// scheme.")
    elif not parsed_url.netloc == "www.mediapart.fr":
        raise HTTPException(status_code=400, detail="We only support www.mediapart.fr website.")

    # Try to retrive article archived localy
    article: schemas.Article = crud.get_article(db, url)

    # If article is not archived
    if (not article):
        scraper = Scraper(settings, url)
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch()
            
            await scraper.login(db, browser)
            if (scraper.is_valid_credentials):
                article = await scraper.save_article(db)
            else:
                raise HTTPException(status_code=503, detail="Credential on {} is no longer valid.".format(parsed_url.netloc))
                

    # Read pdf file
    f = open(article.archived_path, "rb")
    pdf_bytes = f.read()

    return Response(
        content=pdf_bytes, 
        media_type="application/pdf", 
        # To view the file in the browser, use "inline" for the media_type
        headers={"Content-Disposition": "{}; filename={}.pdf".format("attachment" if download==1 else "inline", article.name + ".pdf")}
        )
