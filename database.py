from sqlalchemy.ext.asyncio import create_async_engine,Column,Integer,String,AsyncSession,async_sessionmaker
from sqlalchemy.orm import declarative_base

engine=create_async_engine()
Sessionlocal=async_sessionmaker(autocommit=False,autoflush=False,bind=engine)

class Base(declarative_base):
    pass

def get_db():
    with Sessionlocal as db:
        yield db
    
