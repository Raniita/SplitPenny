from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from splitpenny.crud import bucket as crud
from splitpenny.schemas.bucket import BucketBase, BucketCreateSchema, BucketOutSchema
from splitpenny.main import get_session_db
from splitpenny.services.user import get_current_user, get_user_id_from_username, check_if_user_exists
from splitpenny.services.bucket import add_user_to_bucket, check_bucket_exists, check_if_user_is_in_bucket

router = APIRouter(tags=['Buckets'])

@router.post("/buckets/", response_model=BucketOutSchema)
async def create_bucket(bucket: BucketBase, db: AsyncSession = Depends(get_session_db), username: str = Depends(get_current_user)):
    try: 
        user_id = await get_user_id_from_username(db=db, username=username)
        print(f"User id: {user_id}")
        new_bucket = bucket.model_dump()
        new_bucket["owner_id"] = user_id
        print(f"Model: {new_bucket}")
        res = await crud.create_bucket(db=db, bucket=BucketCreateSchema.model_validate(new_bucket))
        # Add user to bucket_member
        print(f"Adding user {user_id} to bucket {res.id}...")
        await add_user_to_bucket(db=db, user_id=user_id, bucket_id=res.id)
    except Exception as ex:
        print(ex)
        raise HTTPException(status_code=422, detail=f"Error: {str(ex)}")
    return res

@router.get("/buckets/", response_model=list[BucketOutSchema])
async def read_buckets(db:AsyncSession = Depends(get_session_db)):
    return await crud.get_buckets(db=db)

@router.post("/buckets/{bucket_id}/user/{user_id}")
async def add_user_to_bucket_route(bucket_id: int, user_id: int, db: AsyncSession = Depends(get_session_db), username: str = Depends(get_current_user)):
    # Check that bucket exists
    if not await check_bucket_exists(db=db, bucket_id=bucket_id):
        raise HTTPException(status_code=422, detail=f"Error: Bucket {bucket_id} doesnt exists")
    
    # Check that i already a member of the bucket
    print(f"Username User calling this: {username}")
    user_id_caller = await get_user_id_from_username(db=db, username=username)
    if not await check_if_user_is_in_bucket(db=db, bucket_id=bucket_id, user_id=user_id_caller):
        raise HTTPException(status_code=422, detail=f"Error: User {user_id_caller} must be part of the bucket")
    
    # Check that user_id exists, get user object
    if not await check_if_user_exists(db=db, user_id=user_id):
        raise HTTPException(status_code=422, detail=f"Error: User {user_id} doesnt exists")
    
    # Check if user_id is already member of the bucket
    if await check_if_user_is_in_bucket(db=db, bucket_id=bucket_id, user_id=user_id):
        raise HTTPException(status_code=422, detail=f"Error: User {user_id} is already member of the bucket")
    
    # Add user to bucket
    await add_user_to_bucket(db=db, user_id=user_id, bucket_id=bucket_id)
    
    return "OK"