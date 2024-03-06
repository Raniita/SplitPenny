from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from splitpenny.crud import expense as crud
from splitpenny.schemas.expense import ExpenseBase, ExpenseCreateSchema, ExpenseReadSchema, ExpenseSettleUp
from splitpenny.main import get_session_db
from splitpenny.services.user import get_current_user, get_user_id_from_username, check_if_user_exists
from splitpenny.services.bucket import check_bucket_exists, check_if_user_is_in_bucket
from splitpenny.services.expense import calculate_expenses_status, settle_up, calculate_user_status_in_bucket

router = APIRouter(tags=['Buckets'])

@router.post("/buckets/{bucket_id}/status")
async def process_status_bucket(bucket_id: int, show_as_usernames: bool = False, db: AsyncSession = Depends(get_session_db), username: int = Depends(get_current_user)):
    return await calculate_expenses_status(db=db, bucket_id=bucket_id, show_as_usernames=show_as_usernames)

@router.post("/buckets/{bucket_id}/status/me")
async def process_status_bucket_me(bucket_id: int, db: AsyncSession = Depends(get_session_db), username: int = Depends(get_current_user)):
    user_id = await get_user_id_from_username(db=db, username=username)
    return await calculate_user_status_in_bucket(db=db, bucket_id=bucket_id, user_id=user_id)

@router.post("/buckets/{bucket_id}/expense", response_model=ExpenseReadSchema)
async def create_expense_in_bucket(bucket_id: int, expense_data: ExpenseBase, db: AsyncSession = Depends(get_session_db),
                                   username: int = Depends(get_current_user)):
    # Check if bucket exists
    if not await check_bucket_exists(db=db, bucket_id=bucket_id):
        return HTTPException(status_code=422, detail=f"Bucket {bucket_id} doesnt exists")
    
    # Create the Expense
    try:
        # Get user_id from username
        user_id = await get_user_id_from_username(db=db, username=username)
        new_expense = expense_data.model_dump()
        new_expense["bucket_id"] = bucket_id
        new_expense["paid_by_id"] = user_id
        expense = await crud.create_expense(db=db, expense_data=ExpenseCreateSchema.model_validate(new_expense))
        return expense
    except Exception as ex:
        print(ex)
        raise HTTPException(status_code=422, detail=f"Error creating the expense: {str(ex)}")
    
@router.post("/buckets/{bucket_id}/settle/{user_id}")
async def settle_up_to_user(bucket_id: int, user_id: int, info: ExpenseSettleUp, db: AsyncSession = Depends(get_session_db), username: int = Depends(get_current_user)):
    # Check if bucket exists
    if not await check_bucket_exists(db=db, bucket_id=bucket_id):
        return HTTPException(status_code=422, detail=f"Bucket {bucket_id} doesnt exists")
    
    # Check if username is member of the bucket
    user_id_caller = await get_user_id_from_username(db=db, username=username)
    if not await check_if_user_is_in_bucket(db=db, bucket_id=bucket_id, user_id=user_id_caller):
        raise HTTPException(status_code=422, detail=f"Error: User {user_id_caller} must be part of the bucket")
    
    # Check if user_id exists
    if not await check_if_user_exists(db=db, user_id=user_id):
        raise HTTPException(status_code=422, detail=f"Error: User {user_id} doesnt exists")
    
    # Check if user_id is member of the bucket
    if not await check_if_user_is_in_bucket(db=db, bucket_id=bucket_id, user_id=user_id):
        raise HTTPException(status_code=422, detail=f"Error: User {user_id} must be part of the bucket")
    
    # User_id not equals to user_id_caller
    if user_id_caller == user_id:
        raise HTTPException(status_code=422, detail=f"Error: User {user_id} cannot be the same.")
    
    # Add settle_up payment
    await settle_up(db=db, bucket_id=bucket_id, paid_by_id=user_id_caller, paid_to_id=user_id, amount=info.amount, description=info.description)
    
    return "OK"
        
