# Personal Finance App Backend

## Setup

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

- `POST /accounts/`: Create a new account
- `GET /accounts/`: List all accounts
- `POST /upload-transactions/`: Upload CSV transactions for an account
- `GET /accounts/{account_id}/transactions/`: Get transactions for a specific account

## CSV Upload Format

The CSV should have the following columns:
- `date`: Transaction date (YYYY-MM-DD)
- `description`: Transaction description
- `amount`: Transaction amount (positive or negative)
- `category` (optional): Transaction category

Example CSV:
```
date,description,amount,category
2023-05-01,Grocery Shopping,-50.25,Groceries
2023-05-02,Salary,2000.00,Income
```
