import os
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from pprint import pprint
from typing import List, Sequence

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
    db_account = models.Account(name=account.name)
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


@app.get("/accounts/", response_model=List[schemas.Account])
def read_accounts(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> Sequence[models.Account]:
    """Retrieve all accounts"""
    accounts = db.query(models.Account).offset(skip).limit(limit).all()
    return accounts


@app.post("/upload-transactions/{account_id}")
async def upload_transactions(
    file: UploadFile = File(...),
    account_id: int | None = None,
    db: Session = Depends(get_db),
):
    """Upload and parse CSV transactions for an account"""
    # Ensure account exists
    if account_id is None:
        raise HTTPException(status_code=400, detail="Account ID is required")

    account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Save uploaded file temporarily
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as buffer:
        buffer.write(await file.read())

    try:
        # Parse CSV using the new parser
        parser = CSVParser(temp_path)
        parsed_transactions = parser.parse_transactions()

        if not parsed_transactions:
            raise HTTPException(
                status_code=400, detail="No valid transactions found in the CSV file"
            )

        # Create transactions
        pprint(parsed_transactions)
        transactions = []
        for t_data in parsed_transactions:
            transaction = models.Transaction(
                account_id=account_id,
                date=t_data["date"],
                description=t_data["description"],
                amount=t_data["amount"],
                category=t_data.get("category"),
            )
            db.add(transaction)
            transactions.append(transaction)

        # Update account balance if account exists
        if account_id and account is not None:
            total_amount = sum(float(t.amount) for t in transactions)
            account.balance += total_amount

        # Commit transactions
        db.commit()
        for transaction in transactions:
            db.refresh(transaction)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        # Remove temporary file
        os.remove(temp_path)

    # txns = [schemas.Transaction.from_orm(t) for t in transactions]
    # response = schemas.UploadTransactionsResponse(
    #     message=f"Successfully uploaded {len(transactions)} transactions",
    #     transactions=txns,
    # )
    # pprint(response)

    return "ok"


@app.get("/accounts/{account_id}/transactions/")
def read_account_transactions(
    account_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> Sequence[schemas.Transaction]:
    """Retrieve transactions for a specific account"""
    transactions = (
        db.query(models.Transaction)
        .filter(models.Transaction.account_id == account_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    txns = [schemas.Transaction.from_orm(t) for t in list(transactions)]
    return txns
