from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
from datetime import datetime

class TransactionCreate(BaseModel):
    sender: str
    direction: str
    amount: float = Field(..., gt=0, description="Amount must be positive")
    contact_name: str
    phone: str

    @field_validator('direction')
    @classmethod
    def validate_direction(cls, v: str) -> str:
        if v not in ('sent', 'received'):
            raise ValueError("direction must be 'sent' or 'received'")
        return v

class TransactionUpdate(BaseModel):
    sender: Optional[str] = None
    direction: Optional[str] = None
    amount: Optional[float] = Field(None, gt=0)
    contact_name: Optional[str] = None

    @field_validator('direction')
    @classmethod
    def validate_direction(cls, v: str) -> str:
        if v and v not in ('sent', 'received'):
            raise ValueError("direction must be 'sent' or 'received'")
        return v

class LogCreate(BaseModel):
    type: str
    message: str
    transaction_id: Optional[int] = None
    user_id: Optional[int] = None

class LogResponse(LogCreate):
    id: int
    timestamp: datetime

