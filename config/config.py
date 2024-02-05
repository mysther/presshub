from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

from functools import lru_cache

class Credential(BaseModel):
    username: str = 'myemail@domain.tld'
    password: str = 'password'

class Settings(BaseSettings):
    model_config = SettingsConfigDict(secrets_dir='/run/secrets', env_file='.env', env_nested_delimiter='__')

    data_path: str = "./data/"
    mediapart: Credential = None

    SQLALCHEMY_DATABASE_URL: str = "sqlite+pysqlite:///" + data_path + "app.db"

@lru_cache
def get_settings():
    return Settings()