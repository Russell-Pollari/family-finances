from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class TransactionBase(BaseModel):
    date: datetime
    description: str
    amount: float
    category: Optional[str] = None


class TransactionCreate(TransactionBase):
    account_id: int


class Transaction(TransactionBase):
    id: int
    account_id: int

    class Config:
        orm_mode = True


class AccountBase(BaseModel):
    name: str


class AccountCreate(AccountBase):
    pass


class Account(AccountBase):
    id: int
    balance: float
    transactions: List[Transaction] = []

    class Config:
        orm_mode = True


class UploadTransactionsResponse(BaseModel):
    message: str
    transactions: List[Transaction]

    class Config:
        orm_mode = True
