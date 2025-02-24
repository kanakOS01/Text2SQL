from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import auth
from sqlalchemy import text

from backend.database import get_db


app = FastAPI()
ORIGINS = ["*"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/test-db")
async def test_db(db: AsyncSession = Depends(get_db)):
    try:
        res = await db.execute(text("SELECT 'hello world'"))
        print(res.fetchall())
        return {"message": "Database is working"}
    except Exception as e:
        return {"message": f"Database is not working: {e}"}