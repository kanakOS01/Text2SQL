from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import TIMESTAMP


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, server_default=func.now())

    databases = relationship("UserDatabase", back_populates="owner")

    def __repr__(self) -> str:
        return f"<User(id={self.id!r}, username={self.username!r})"
    

class UserDatabase(Base):
    __tablename__ = "user_databases"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    db_name: Mapped[str] = mapped_column(unique=True, nullable=False)
    db_uri: Mapped[str] = mapped_column(nullable=False)
    db_schema: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, server_default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)
    
    owner = relationship("User", back_populates="databases")

    def __repr__(self) -> str:
        return f"<UserDatabase(id={self.id!r}, db_name={self.db_name!r})"