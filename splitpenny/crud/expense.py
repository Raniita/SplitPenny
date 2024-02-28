from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from splitpenny.database.models import Expense
from splitpenny.schemas.expense import ExpenseCreateSchema, ExpenseReadSchema

async def create_expense(db: AsyncSession, expense_data: ExpenseCreateSchema) -> ExpenseReadSchema:
    new_expense = Expense(**expense_data.model_dump())
    db.add(new_expense)
    await db.commit()
    await db.refresh(new_expense)
    return ExpenseReadSchema.model_validate(new_expense)

async def get_expenses(db: AsyncSession) -> list[ExpenseReadSchema]:
    async with db as session:
        result = await session.execute(select(Expense))
        expenses = result.scalar().all()
        return [ExpenseReadSchema.model_validate(expense) for expense in expenses]
    
async def get_expense(db: AsyncSession, expense_id: int) -> ExpenseReadSchema:
    async with db as session:
        result = await session.execute(select(Expense).filter(Expense.id == expense_id))
        expense = result.scalars().first()
        if expense:
            return ExpenseReadSchema.model_validate(expense)
        else: 
            return None
        
async def update_expense(db: AsyncSession, expense_id: int, expense_data: ExpenseCreateSchema) -> ExpenseReadSchema:
    async with db as session:
        result = await session.execute(select(Expense).filter(Expense.id == expense_id))
        expense = result.scalars().first()
        if expense:
            update_data = expense_data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(expense, key, value)
            await db.commit()
            return ExpenseReadSchema.model_validate(expense)
        else:
            return None

async def delete_expense(db: AsyncSession, expense_id: int):
    async with db as session:
        result = await session.execute(select(Expense).filter(Expense.id == expense_id))
        expense = result.scalars().first()
        if expense:
            await db.delete(expense)
            await db.commit()
            return True
        else:
            return False
