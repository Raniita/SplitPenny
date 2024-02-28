from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from splitpenny.crud import expense as crud
from splitpenny.schemas.expense import ExpenseBase, ExpenseCreateSchema, ExpenseReadSchema
from splitpenny.main import get_session_db
from splitpenny.services.user import get_current_user, get_user_id_from_username
from splitpenny.services.bucket import check_bucket_exists

router = APIRouter(tags=['Buckets'])

@router.post("/buckets/{bucket_id}/status")
async def process_status_bucket(bucket_id:int):
    return ""

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
        
