from fastapi import FastAPI, Response, Depends
from playwright.async_api import async_playwright
from sqlalchemy.orm import Session

from typing import Union, Annotated
from urllib.parse import urlparse
from os.path import isfile

import json

from config.config import Settings, get_settings
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


@app.get("/")
async def hello(settings: Annotated[Settings, Depends(get_settings)]):
    return settings

@app.get("/articles/", response_model=list[schemas.Article])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    articles = crud.get_articles(db, skip=skip, limit=limit)
    return articles

@app.get("/{url:path}")
async def catch_all(settings: Annotated[Settings, Depends(get_settings)], url: Union[str, None] = None, download: Union[int, None] = None):
    
    parsed_url = urlparse(url)
    if not parsed_url.scheme and not parsed_url.netloc:
        return Response(
            content=json.dumps({"status_code": "400", "message": "Please, add an Mediapart URL in the path."}),
            media_type="application/json",
            status_code=400
        )

    if not parsed_url.scheme == "https":
        return Response(
            content=json.dumps({"status_code": "400", "message": "We only support https:// scheme."}),
            media_type="application/json",
            status_code=400
        )

    if not parsed_url.netloc == "www.mediapart.fr":
        return Response(
            content=json.dumps({"status_code": "400", "message": "We only support www.mediapart.fr website."}),
            media_type="application/json",
            status_code=400
        )

    filename = parsed_url.path.split("/")[-1] + ".pdf"

    if (isfile(settings.data_path + filename)):
        f = open(settings.data_path + filename, "rb")
        pdf_bytes = f.read()
            
    else:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch()

            api_context = await browser.new_context(base_url="https://www.mediapart.fr")
            await api_context.request.post("https://www.mediapart.fr/login_check", form={
                    'name': settings.mediapart.username,
                    'password': settings.mediapart.password
                })

            page = await api_context.new_page()
            await page.goto(url)
            pdf_bytes = await page.pdf()
            await browser.close()

        f = open(settings.data_path + filename, "wb")
        f.write(pdf_bytes)
        f.close()

    return Response(
        content=pdf_bytes, 
        media_type="application/pdf", 
        # To view the file in the browser, use "inline" for the media_type
        headers={"Content-Disposition": "{}; filename={}.pdf".format("attachment" if download==1 else "inline", filename)}
        )
