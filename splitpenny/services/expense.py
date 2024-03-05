from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from collections import defaultdict
from typing import Dict, List
from decimal import Decimal

from splitpenny.database.models import Bucket, User

async def calculate_expenses_status(db: AsyncSession, bucket_id: int) -> Dict[str, Dict]:
    # Fetch the bucket, its members, and expenses
    bucket_result = await db.execute(select(Bucket).where(Bucket.id == bucket_id).options(selectinload(Bucket.members), selectinload(Bucket.expenses)))
    bucket = bucket_result.scalars().first()
    if not bucket:
        return {"error": "Bucket not found"}
    
    total_expenses = sum(expense.amount for expense in bucket.expenses)
    split_amount = total_expenses/ len(bucket.members) if bucket.members else 0
    
    # Initialize data structures to keep track of payments and dues
    payments = defaultdict(lambda: Decimal(0))               # How much each user has paid
    dues = defaultdict(lambda: split_amount)    # How much user owes
    
    for expense in bucket.expenses:
        payments[expense.paid_by_id] += Decimal(expense.amount)
        dues[expense.paid_by_id] -= split_amount
        
    # Calculate final balances
    balances = {
        member.username: payments[member.id] - dues[member.id] for member in bucket.members
    }
    
    return {
        "total_expenses": total_expenses,
        "balances": balances
    }