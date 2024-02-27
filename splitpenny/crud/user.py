from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from splitpenny.database.models import User
from splitpenny.schemas.user import UserInSchema, UserOutSchema

async def create_user(db: AsyncSession, user: UserInSchema) -> UserOutSchema:
    db_user = User(**user.model_dump())
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return UserOutSchema.model_validate(db_user)

async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[UserOutSchema]:
    async with db as session:
        result = await session.execute(select(User).offset(skip).limit(limit))
        users = result.scalars().all()
        return [UserOutSchema.model_validate(user) for user in users]
