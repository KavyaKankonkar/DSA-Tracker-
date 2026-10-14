from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession,async_sessionmaker
from sqlalchemy.orm import declarative_base
import os
from dotenv import load_dotenv

load_dotenv(override=True)

engine=create_async_engine(os.getenv("DATABASE_URL"))
Sessionlocal=async_sessionmaker(autocommit=False,autoflush=False,bind=engine)

Base = declarative_base()

async def get_db():
    async with Sessionlocal as db:
        yield db

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

