from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    DATABASE_URL_NON_ASYNC: str

    class Config:
        env_file = '.env'

settings = Settings()