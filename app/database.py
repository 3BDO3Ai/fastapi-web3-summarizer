from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./summarizer.db")
if DB_URL.startswith("postgresql://"):
    DATABASE_URL = DB_URL.replace("postgresql://", "postgresql+asyncpg://")
else:
    DATABASE_URL = DB_URL

engine = create_async_engine(
    DATABASE_URL, 
    future=True,
    echo=True
)

SessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autocommit=False, 
    autoflush=False
)

Base = declarative_base()

async def get_db():
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()
