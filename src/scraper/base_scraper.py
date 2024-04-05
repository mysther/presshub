from datetime import datetime
from config.config import Settings
from playwright.async_api import Browser, BrowserContext
from urllib.parse import urlparse, unquote

from sqlalchemy.orm import Session
from sql import crud, schemas


class Scraper(object):
    username: str
    password: str
    browser_context: BrowserContext
    is_valid_credentials: bool
    
    def __new__(cls, settings: Settings, url: str):
        parsed_url = urlparse(url)

        subclass_map = {subclass.hostname: subclass for subclass in cls.__subclasses__()}
        subclass = subclass_map[parsed_url.hostname]
        instance = super(Scraper, subclass).__new__(subclass)
        return instance
    
    async def login(self, db: Session, browser: Browser):
        pass

    async def save_article(self, db: Session):
        pass

class ScraperMediapart(Scraper):
    hostname = 'www.mediapart.fr'

    def __init__(self, settings: Settings, url: str):
        self.url = url
        self.is_valid_credentials = True
        self.username = settings.mediapart.username
        self.password = settings.mediapart.password

    async def login(self, db: Session, browser: Browser):
        website_session = crud.get_website_session(db, self.hostname)

        if (website_session):
            self.browser_context = await browser.new_context(storage_state=website_session.storage_state)
        else:
            self.browser_context = await browser.new_context()
            
            await self.browser_context.request.post("https://www.mediapart.fr/login_check", form={
                    'name': self.username,
                    'password': self.password
                })
            
            storage_state = await self.browser_context.storage_state()
            
            if (unquote(storage_state['cookies'][0]['value']) == '{"login_error":["login.bad_credentials"]}'):
                self.is_valid_credentials = False
                return
            self.is_valid_credentials = True
            
            website_session: schemas.WebsiteSession = schemas.WebsiteSession(
                hostname=self.hostname,
                storage_state=storage_state
            )
            crud.save_website_session(db, website_session)

    async def save_article(self, db):
        page = await self.browser_context.new_page()
        await page.goto(self.url)
        pdf_bytes = await page.pdf()
        await self.browser_context.close()

        article: schemas.Article = schemas.ArticleCreate(
            url=self.url,
            writen_timestamp=datetime.now()
            )
        
        article = crud.save_article(db, article)

        f = open(article.archived_path, "wb")
        f.write(pdf_bytes)
        f.close()

        return article