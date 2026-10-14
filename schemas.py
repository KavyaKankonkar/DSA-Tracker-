from pydantic import BaseModel, ConfigDict, Field,EmailStr
from datetime import datetime
from typing import Literal

class UserBase(BaseModel):
    user_name:str =Field(min_length=1,max_length=50)
    email: EmailStr 

class UserCreate(UserBase):
    hashed_password :str =Field(min_length=8)

class UserResponse(UserBase):
    model_config=ConfigDict(from_attributes=True)
    id:int
    created_at: datetime

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: int | None = None

class TagBase(BaseModel):
    name: str=Field(min_length=1,max_length=30) 

class TagCreate(TagBase):
    pass

class TagResponse(TagBase):
    model_config=ConfigDict(from_attributes=True)
    id:int 


class PatternBase(BaseModel):
    name: str = Field(min_length=1, max_length=50)

class PatternCreate(PatternBase):
    pass

class PatternResponse(PatternBase):
    model_config = ConfigDict(from_attributes=True)
    id: int

class ProblemBase(BaseModel):
    problem_name: str=Field(min_length=1,max_length=500)
    status: Literal['solved', 'failed', 'attempted'] | None = "attempted" 
    description: str =Field( min_length=1,max_length=500)
    
class ProblemCreate(ProblemBase):
    tags_ids: list[int] =Field(default_factory=list)
    pattern_ids: list[int]  =Field(default_factory=list)

class ProblemResponse(ProblemBase):
    model_config =ConfigDict(from_attributes=True)
    id:int
    user_id : int 
    created_at: datetime   
    tags: list[TagResponse]  
    patterns: list[PatternResponse]

class ProblemUpdate(BaseModel):
    problem_name: str | None = Field(default=None, min_length=1, max_length=500)
    description: str | None = Field(default=None, min_length=1, max_length=500)
    status: Literal['solved', 'failed', 'attempted'] | None = None 
    tags_ids: list[int] | None = None
    pattern_ids: list[int] | None = None

class AttemptBase(BaseModel):
    problem_id:int
    time_taken:int | None =None
    status : Literal['solved','failed','attempted']
    notes: str | None =None

class AttemptCreate(AttemptBase):
    pass

class AttemptResponse(AttemptBase):
    id:int
    model_config=ConfigDict(from_attributes=True)
    user_id:int 
    attempted_at:datetime
