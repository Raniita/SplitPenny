from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import bcrypt

from splitpenny.database.models import User
from splitpenny.utils.jwt import verify_access_token

async def authenticate_user(db: AsyncSession, username: str, password: str):
    async with db as session:
        result = await session.execute(select(User).filter(User.username == username))
        user = result.first()
        if user is None:
            return False
        user_data = user[0]
        if not verify_password(password, user_data.password):
            return False
        return user_data
    
def get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="token"))):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    
    return verify_access_token(token=token, credentials_exception=credentials_exception)
    
def get_password_hash(password: str):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

async def get_user_id_from_username(db: AsyncSession, username: str):
    async with db as session:
        result = await session.execute(select(User.id).filter(User.username == username))
        user_id = result.scalars().first()
        if user_id is None:
            raise Exception("Not found")
        return user_id
