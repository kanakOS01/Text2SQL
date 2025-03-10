from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from backend.config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = sessionmaker(bind=engine, autoflush=False, class_=AsyncSession)


async def get_db():
    async with AsyncSessionLocal() as db:
        await db.execute(text("PRAGMA foreign_keys = ON;"))
        yield db
