import os
from fastapi import FastAPI, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Union, Sequence, Optional

from app import models, schemas
from app.database import engine, get_db
from app.csv_parser import CSVParser

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.post("/accounts/", response_model=schemas.Account)
def create_account(
    account: schemas.AccountCreate, db: Session = Depends(get_db)
) -> models.Account:
    """Create a new account"""
    db_account = models.Account(name=account.name, balance=0)
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


@app.get("/accounts/", response_model=List[schemas.Account])
def read_accounts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve all accounts"""
    accounts = db.query(models.Account).offset(skip).limit(limit).all()
    return accounts


@app.post("/upload-transactions/{account_id}", response_model=schemas.Account)
async def upload_transactions(
    file: UploadFile,
    account_id: int,
    db: Session = Depends(get_db),
):
    """Upload and parse CSV transactions for an account"""
    # Ensure account exists
    account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Save uploaded file temporarily
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as buffer:
        buffer.write(await file.read())

    try:
        # Parse CSV
        parser = CSVParser(temp_path)
        parsed_transactions = parser.parse_transactions()

        if not parsed_transactions:
            raise HTTPException(
                status_code=400, detail="No valid transactions found in the CSV file"
            )

        # Create transactions
        transactions = []
        total_amount = 0.0
        for t_data in parsed_transactions:
            credit = t_data.get("credit")
            debit = t_data.get("debit")
            amount = (credit or 0.0) - (debit or 0.0)
            transaction = models.Transaction(
                account_id=account_id,
                date=t_data["date"],
                description=t_data["description"],
                credit=credit,
                debit=debit,
                category=t_data.get("category"),
            )
            total_amount += amount
            db.add(transaction)
            transactions.append(transaction)

        # Update account balance
        if account.balance is None:
            account.balance = 0
        account.balance += total_amount
        # Commit transactions
        db.commit()
        db.refresh(account)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        # Remove temporary file
        os.remove(temp_path)

    return account


@app.get(
    "/accounts/{account_id}/transactions/", response_model=List[schemas.Transaction]
)
def read_account_transactions(
    account_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> Sequence[models.Transaction]:
    """Retrieve transactions for a specific account"""
    transactions = (
        db.query(models.Transaction)
        .filter(models.Transaction.account_id == account_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return transactions


@app.delete("/accounts/{account_id}")
def delete_account(account_id: int, db: Session = Depends(get_db)):
    """Delete an account and all its transactions"""
    # Get the account
    account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Delete all transactions associated with the account
    db.query(models.Transaction).filter(models.Transaction.account_id == account_id).delete()
    
    # Delete the account
    db.delete(account)
    db.commit()
    
    return {"message": "Account and all associated transactions deleted successfully"}


def clean_float(value) -> Optional[float]:
    """Clean and validate float values"""
    if value is None:
        return None
    try:
        # Convert to float and check if it's a valid JSON number
        cleaned = float(value)
        if not (float("-inf") < cleaned < float("inf")):
            return None
        return cleaned
    except (ValueError, TypeError):
        return None


@app.post(
    "/preview-transactions/{account_id}", response_model=List[schemas.Transaction]
)
async def preview_transactions(
    file: UploadFile,
    account_id: int,
    db: Session = Depends(get_db),
):
    """Preview CSV transactions before importing"""
    # Ensure account exists
    account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Save uploaded file temporarily
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as buffer:
        buffer.write(await file.read())

    try:
        # Parse CSV
        parser = CSVParser(temp_path)
        parsed_transactions = parser.parse_transactions()

        if not parsed_transactions:
            raise HTTPException(
                status_code=400, detail="No valid transactions found in the CSV file"
            )

        # Convert to schema format
        preview_transactions = []
        for t_data in parsed_transactions:
            # Clean numeric values
            credit = clean_float(t_data.get("credit"))
            debit = clean_float(t_data.get("debit"))

            # Skip transactions with invalid amounts
            if credit is None and debit is None:
                continue

            try:
                transaction = schemas.Transaction(
                    account_id=account_id,
                    date=t_data["date"],
                    description=t_data["description"],
                    credit=credit,
                    debit=debit,
                    category=t_data.get("category", "Other"),
                )
                preview_transactions.append(transaction)
            except (ValueError, TypeError) as e:
                # Skip invalid transactions but continue processing
                continue

        if not preview_transactions:
            raise HTTPException(
                status_code=400,
                detail="No valid transactions found after cleaning data",
            )

        return preview_transactions

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        # Remove temporary file
        os.remove(temp_path)


@app.post("/import-transactions/{account_id}", response_model=schemas.Account)
async def import_transactions(
    account_id: int,
    import_data: schemas.TransactionImportRequest,
    db: Session = Depends(get_db),
):
    """Import selected and edited transactions"""
    # Ensure account exists
    account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    try:
        # Create transactions
        total_amount = 0.0
        for t_data in import_data.transactions:
            credit = clean_float(t_data.credit)
            debit = clean_float(t_data.debit)
            amount = (credit or 0.0) - (debit or 0.0)

            transaction = models.Transaction(
                account_id=account_id,
                date=t_data.date,
                description=t_data.description,
                credit=credit,
                debit=debit,
                category=t_data.category,
            )
            total_amount += amount
            db.add(transaction)

        # Update account balance
        if account.balance is None:
            account.balance = 0
        account.balance += total_amount

        # Commit transactions
        db.commit()
        db.refresh(account)

        return account

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
