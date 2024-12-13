from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class TransactionBase(BaseModel):
    date: datetime
    description: str
    credit: Optional[float] = None
    debit: Optional[float] = None
    category: Optional[str] = "Other"

    @property
    def amount(self) -> float:
        """Calculate the net amount (credit - debit)"""
        credit = self.credit or 0.0
        debit = self.debit or 0.0
        return credit - debit


class TransactionCreate(TransactionBase):
    account_id: int


class Transaction(TransactionBase):
    id: Optional[int] = None
    account_id: int

    class Config:
        orm_mode = True


class AccountBase(BaseModel):
    name: str


class AccountCreate(AccountBase):
    pass


class Account(AccountBase):
    id: int
    balance: Optional[float] = None
    transactions: List[Transaction] = []

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class UploadTransactionsResponse(BaseModel):
    message: str
    transactions: List[Transaction]

    class Config:
        orm_mode = True


class TransactionImportRequest(BaseModel):
    transactions: List[TransactionCreate]


class ImportResponse(BaseModel):
    account: Account
    imported_count: int
    duplicate_count: int
