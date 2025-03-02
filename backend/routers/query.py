from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select
from sqlalchemy import text

from backend.database import get_db
from backend.routers.databases import get_database_schema
from backend.text2sql import Text2SQLModel
from backend.models import UserDatabase
from backend.utils import extract_scheme

router = APIRouter(prefix="/query", tags=["Text to SQL Query"])


@router.post("/{db_id}/generate_sql")
async def generate_sql(db_id: int, text_query: str, db: AsyncSession = Depends(get_db)):
    """
    Generate SQL query from natural language question
    """
    try:
        result = await db.execute(select(UserDatabase.db_uri).filter(UserDatabase.id == db_id))
        db_uri = result.scalar_one_or_none()
        if not db_uri:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Database not found")
        
        db_scheme = extract_scheme(db_uri)
        schema = await get_database_schema(db_id, db)
        text2sql_model = Text2SQLModel(db_scheme, schema)
        response = text2sql_model.infer(text_query)
        return {"sql_query": response}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e}")
    

@router.post("/{db_id}/execute_sql")
async def execute_sql(db_id: int, sql_query: str, db: AsyncSession = Depends(get_db)):
    """
    Execute SQL query on database
    """
    try:
        result = await db.execute(select(UserDatabase.db_uri).filter(UserDatabase.id == db_id))
        db_uri = result.scalar_one_or_none()
        if not db_uri:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Database not found")

        engine = create_async_engine(db_uri, echo=False, future=True)
        async with engine.begin() as conn:
            result = await conn.execute(text(sql_query))
            response = result.mappings().all()
        
        return {"data": response}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e}")
