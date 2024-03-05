from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum

class SplitType(str, Enum):
    EQUALLY = 'Equally'
    SETTLEMENT = "Settlement"

class ExpenseBase(BaseModel):
    description: str = Field(..., max_length=255)
    amount: float
    split_type: SplitType
    
    @validator('amount')
    def amount_must_be_positive(cls, value):
        if value <= 0:
            raise ValueError('amount must be greater than zero')
        return value

class ExpenseCreateSchema(ExpenseBase):
    bucket_id: int
    paid_by_id: int
    
    class Config:
        from_attributes = True
    
class ExpenseReadSchema(ExpenseBase):
    id: int
    created_at: datetime
    paid_by_id: int | None = None
    
    class Config:
        from_attributes = True
        
class ExpenseSettleUp(BaseModel):
    description: str = Field(..., max_length=255)
    amount: float
    
    @validator('amount')
    def amount_must_be_positive(cls, value):
        if value <= 0:
            raise ValueError('amount must be greater than zero')
        return value
