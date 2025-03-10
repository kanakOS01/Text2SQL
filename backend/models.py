from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import TIMESTAMP


class Base(DeclarativeBase):
    pass


class UserDatabase(Base):
    __tablename__ = "user_databases"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    db_name: Mapped[str] = mapped_column(unique=True, nullable=False)
    db_uri: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, server_default=func.now())

    def __repr__(self) -> str:
        return f"<UserDatabase(id={self.id!r}, db_name={self.db_name!r}, db_uri={self.db_uri!r})>"
