from fastapi import HTTPException
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from splitpenny.database.models import Bucket, User

async def check_bucket_exists(db: AsyncSession, bucket_id: int) -> bool:
    async with db as session:
        result = await session.execute(select(Bucket).filter(Bucket.id == bucket_id))
        bucket = result.scalars().first()
        return bucket is not None
    
async def check_if_user_is_in_bucket(db: AsyncSession, bucket_id: int, user_id: int) -> bool:
    async with db as session:
        user_result = await session.execute(select(User).where(User.id == user_id))
        bucket_result = await session.execute(select(Bucket).where(Bucket.id == bucket_id).options(selectinload(Bucket.members)))
        user = user_result.scalars().first()
        bucket = bucket_result.scalars().first()
        
        if not user or not bucket:
            raise HTTPException(status_code=422, detail=f"Error: user_id {user_id} or bucket_id {bucket_id} not found.")
        
        if user not in bucket.members:
            return False
        else:
            return True

async def add_user_to_bucket(db: AsyncSession, user_id: int, bucket_id: int) -> bool:
    async with db as session:
        user_result = await session.execute(select(User).where(User.id == user_id))
        bucket_result = await session.execute(select(Bucket).where(Bucket.id == bucket_id).options(selectinload(Bucket.members)))
        user = user_result.scalars().first()
        bucket = bucket_result.scalars().first()
        
        if not user or not bucket:
            return False
        
        print(f"User: {user.id} to bucket {bucket.id}")
        
        if user not in bucket.members:
            bucket.members.append(user)
            await session.commit()
            return True
        return False
