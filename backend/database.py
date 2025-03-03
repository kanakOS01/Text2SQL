from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from backend.config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = sessionmaker(bind=engine, autoflush=False, class_=AsyncSession)


async def get_db():
    async with AsyncSessionLocal() as db:
        await db.execute(text("PRAGMA foreign_keys = ON;"))
        yield db