from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from splitpenny.crud import bucket as crud
from splitpenny.schemas.bucket import BucketInSchema, BucketOutSchema
from splitpenny.main import get_session_db

router = APIRouter()

@router.post("/buckets/", response_model=BucketOutSchema)
async def create_bucket(bucket: BucketInSchema, db: AsyncSession = Depends(get_session_db)):
    return await crud.create_bucket(db=db, bucket=bucket)

@router.get("/buckets/", response_model=list[BucketOutSchema])
async def read_buckets(db:AsyncSession = Depends(get_session_db)):
    return await crud.get_buckets(db=db)