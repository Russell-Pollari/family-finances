from datetime import datetime
from typing import List

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, DeclarativeBase


class Base(DeclarativeBase):
    pass


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    name: Mapped[str] = Column(String, unique=True, index=True)
    balance: Mapped[float] = Column(Float, default=0.0)

    transactions: Mapped[List["Transaction"]] = relationship(
        "Transaction", back_populates="account"
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    account_id: Mapped[int] = Column(Integer, ForeignKey("accounts.id"))
    date: Mapped[datetime] = Column(DateTime, default=datetime.utcnow)
    description: Mapped[str] = Column(String)
    credit: Mapped[float | None] = Column(Float, nullable=True)
    debit: Mapped[float | None] = Column(Float, nullable=True)
    category: Mapped[str | None] = Column(String, nullable=True)

    account: Mapped[Account] = relationship("Account", back_populates="transactions")

    @property
    def amount(self) -> float:
        """Calculate the net amount (credit - debit)"""
        credit = self.credit or 0.0
        debit = self.debit or 0.0
        return credit - debit
