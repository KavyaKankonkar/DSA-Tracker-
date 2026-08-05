from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt,TokenData,form_data
from passlib.context import CryptContext
import os
from dotenv import load_dotenv
from fastapi import HTTPException,Depends
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models import User
from schemas import UserCreate

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password,hashed_password)

def create_access_token(data: dict) -> str:
    to_encode=data.copy()
    expire=datetime.now(timezone.utc)+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["exp"]=expire
    encoded_jwt=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token:str) ->TokenData: 
    try:
        decoded_jwt=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401,detail="Invalid or expired token")
    user_id=decoded_jwt.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401,detail="Key not found")
    return TokenData(user_id=int(user_id))
            

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    token_data=decode_token(token)
  
    result=await db.execute(select(User).where(User.id==token_data.user_id))
    user=result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401,detail="User not found")
    return user

async def login(form_data: OAuth2PasswordRequestForm = Depends() ,
                db: AsyncSession = Depends(get_db)) :

    result=await db.execute(select(User).where(User.name==form_data.username))
    user=result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404,detail="Incorrect Username")

    if not verify_password(form_data.password,user.hashed_password):
        raise HTTPException(status_code=401,detail="Wrong password")

    access_token=create_access_token(data={"sub":str(user.id)})
    return {"access_token":access_token,"token_type":"bearer"}

async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    user_n=user_data.username
    user_p=user_data.password
    user_e=user_data.email

    result = await db.execute(select(User).where(User.name == user_n))
    existing_user = result.scalar_one_or_none()
    if existing_user is not None:
        raise HTTPException(status_code=409, detail="Username already exists")

    hp=hash_password(user_p)
    new_user=User(name=user_n,hashed_password=hp,email=user_e)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    access_token=create_access_token(data={"sub":str(new_user.id)})
    return {"access_token":access_token,"token_type":"bearer"}

    