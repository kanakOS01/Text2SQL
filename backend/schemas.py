from typing import Optional
from pydantic import BaseModel


class Database(BaseModel):
    id: int
    db_name: str
    db_uri: str