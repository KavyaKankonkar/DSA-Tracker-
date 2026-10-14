from sqlalchemy import Column,String,Integer,DateTime,ForeignKey,Table,UniqueConstraint
from database import Base
from datetime import datetime,timezone
from sqlalchemy.orm import relationship 

class User(Base):
    __tablename__="users"

    id =Column(Integer,primary_key=True)
    user_name= Column(String,nullable=False)
    email=Column(String,nullable=False,unique=True)
    hashed_password=Column(String,nullable=False)
    created_at=Column(DateTime(timezone=True),default =lambda : datetime.now(timezone.utc))
    problems=relationship("Problem",back_populates="owner")
    attempts=relationship("Attempt",back_populates="user")

problem_tags=Table(
        "problem_tags",
        Base.metadata,
        Column("problem_id",Integer,ForeignKey("problems.id"),primary_key=True),
        Column("tag_id",Integer,ForeignKey("tags.id"),primary_key=True)
        )

problem_patterns=Table(
    "problem_patterns",
    Base.metadata,
    Column("problem_id",Integer,ForeignKey("problems.id"),primary_key=True),
    Column("pattern_id",Integer,ForeignKey("patterns.id"),primary_key=True)
)

class Tag(Base):
    __tablename__="tags"

    id=Column(Integer,primary_key=True)
    name=Column(String,nullable=False,unique=True)
    problems=relationship("Problem",secondary=problem_tags,back_populates="tags")

class Pattern(Base):
    __tablename__="patterns"

    id=Column(Integer,primary_key=True)
    name=Column(String,nullable=False,unique=True)
    problems=relationship("Problem",secondary=problem_patterns,back_populates="patterns")

class Problem(Base):
    __tablename__="problems"

    id = Column(Integer,primary_key=True)
    problem_name=Column(String,nullable=False)
    description= Column(String)
    status = Column(String, nullable=True, default="attempted") 
    created_at =Column(DateTime(timezone=True),default =lambda : datetime.now(timezone.utc))
    user_id=Column(Integer,ForeignKey("users.id"),nullable=False)
    owner= relationship("User",back_populates="problems")
    tags=relationship("Tag",secondary=problem_tags,back_populates="problems")
    patterns=relationship("Pattern",secondary=problem_patterns,back_populates="problems")
    attempts=relationship("Attempt",back_populates="problems",cascade="all, delete-orphan", passive_deletes=True)
    
class Attempt(Base):
    __tablename__="attempts"
    id=Column(Integer,primary_key=True)
    time_taken=Column(Integer,nullable=True)
    status=Column(String,nullable=False)
    notes=Column(String)
    attempted_at=Column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc))
    problem_id=Column(Integer,ForeignKey("problems.id",ondelete="CASCADE"))
    user_id=Column(Integer,ForeignKey("users.id"))
    problems=relationship("Problem",back_populates="attempts")
    user=relationship("User",back_populates="attempts")
    