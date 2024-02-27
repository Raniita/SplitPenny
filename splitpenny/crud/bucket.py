from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from splitpenny.database.models import Bucket
from splitpenny.schemas.bucket import BucketInSchema, BucketOutSchema

async def create_bucket(db: AsyncSession, bucket: BucketInSchema):
    db_bucket = Bucket(**bucket.model_dump())
    db.add(db_bucket)
    await db.commit()
    await db.refresh(db_bucket)
    return BucketOutSchema.model_validate(db_bucket)

async def get_buckets(db: AsyncSession) -> list[BucketOutSchema]:
    async with db as session:
        result = await session.execute(select(Bucket))
        buckets = result.scalars().all()
        return [BucketOutSchema.model_validate(bucket) for bucket in buckets]
