from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import text
from sqlalchemy.future import select
from typing import List

from backend.database import get_db
from backend.models import UserDatabase
from backend import schemas
from backend.utils import check_valid_uri, extract_scheme

router = APIRouter(prefix="/databases", tags=["Databases"])


@router.get("/", response_model=List[schemas.Database])
async def get_databases(db: AsyncSession = Depends(get_db)):
    """
    Returns a list of all user-added databases.
    """
    try:
        result = await db.execute(select(UserDatabase))
        databases = result.scalars().all()
        return databases
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e}")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_database(db_name: str, db_uri: str, db: AsyncSession = Depends(get_db)):
    """
    Create a new database.
    """
    if not check_valid_uri(db_uri):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid database URI")

    try:
        existing_db = await db.execute(select(UserDatabase).filter(UserDatabase.db_uri == db_uri))
        if existing_db.scalars().first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Database URI already exists")

        new_db = UserDatabase(db_name=db_name, db_uri=db_uri)
        db.add(new_db)
        await db.commit()
        await db.refresh(new_db)

        return {"message": "Database created successfully", "id": new_db.id}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e}")


@router.delete("/{db_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_database(db_id: int, db: AsyncSession = Depends(get_db)):
    """
    Delete a database by ID.
    """
    try:
        db_entry = await db.get(UserDatabase, db_id)
        if not db_entry:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Database not found")

        await db.delete(db_entry)
        await db.commit()
        return {"message": "Database deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e}")


@router.get("/{db_id}/schema")
async def get_database_schema(db_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get the schema of a database by ID.
    """
    try:
        result = await db.execute(select(UserDatabase.db_uri).filter(UserDatabase.id == db_id))
        db_uri = result.scalar_one_or_none()
        if not db_uri:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Database not found")

        if db_uri.startswith("mysql://"):
            db_uri = db_uri.replace("mysql://", "mysql+aiomysql://") 

        engine = create_async_engine(db_uri, echo=False, future=True)
        async with engine.begin() as conn:
            db_scheme = extract_scheme(db_uri)
            
            if "mysql" in db_scheme:
                schema_query = text("""
                    SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT, COLUMN_KEY 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :table_name;
                """)
                table_query = text("SHOW TABLES;")
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported database type: {db_scheme}")
            
            result = await conn.execute(table_query)
            tables = [row[0] for row in result.fetchall()]
            
            schema_details = {}

            # Fetch schema details for each table
            for table in tables:
                table_schema_result = await conn.execute(schema_query, {"table_name": table})
                schema_details[table] = [
                    {
                        "column_name": row[0],
                        "data_type": row[1],
                        "nullable": row[2],
                        "default_value": row[3],
                        "key": row[4] if len(row) > 4 else None  # MySQL-specific column key
                    }
                    for row in table_schema_result.fetchall()
                ]

        return {"schema": schema_details}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {e}")