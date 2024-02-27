from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from splitpenny.crud import user as crud
from splitpenny.schemas.user import UserInSchema, UserOutSchema
from splitpenny.main import get_session_db

router = APIRouter()

@router.post("/users/", response_model=UserOutSchema)
async def create_user(user: UserInSchema, db: AsyncSession = Depends(get_session_db)):
    return await crud.create_user(db=db, user=user)

@router.get("/users/", response_model=list[UserOutSchema])
async def read_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_session_db)):
    return await crud.get_users(db, skip=skip, limit=limit)