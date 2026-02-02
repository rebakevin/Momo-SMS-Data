from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Transaction:
    amount: float
    direction: str
    id: Optional[int] = None
    date: Optional[datetime] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    status: int = 1
    service_center: str = ""
    read_status: Optional[str] = None # 'read' is a keyword, mapped to read_status
    locked: int = 0
    date_sent: Optional[datetime] = None
    readable_date: Optional[str] = None
    contact_name: Optional[str] = None
    transaction_id: Optional[int] = None # External/Legacy ID
    balance_after: float = 0.0
    category_id: Optional[int] = None
    user_id: Optional[int] = None

@dataclass
class User:
    name: str
    phone_number: str
    id: Optional[int] = None

@dataclass
class TransactionCategory:
    name: str
    description: str
    id: Optional[int] = None
