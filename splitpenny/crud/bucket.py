from sqlalchemy.orm import selectinload 
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from splitpenny.database.models import Bucket
from splitpenny.schemas.bucket import BucketCreateSchema, BucketOutSchema

async def create_bucket(db: AsyncSession, bucket: BucketCreateSchema):
    db_bucket = Bucket(**bucket.model_dump())
    db.add(db_bucket)
    await db.commit()
    await db.refresh(db_bucket)
    return BucketOutSchema.model_validate(db_bucket)

async def get_buckets(db: AsyncSession) -> list[BucketOutSchema]:
    async with db as session:
        result = await session.execute(select(Bucket).options(selectinload(Bucket.members)))
        buckets = result.scalars().all()
        buckets_out = []
        for bucket in buckets:
            bucket_dict = bucket.__dict__.copy()
            bucket_dict['members_id'] = [member.id for member in bucket.members]
            bucket_out_schema = BucketOutSchema.model_validate(bucket_dict)
            buckets_out.append(bucket_out_schema)
        return buckets_out

