# Personal Finance Tracker

## Overview
A full-stack personal finance web application that allows users to:
- Create multiple financial accounts
- Upload transaction data via CSV
- View account balances
- Track transaction history

## Technology Stack
- **Backend**: FastAPI (Python)
- **Database**: SQLite
- **Frontend**: React

## Features
- Create new accounts
- Upload CSV transactions
- View account balances
- List transactions per account

## Setup and Installation

### Backend Setup
1. Navigate to the backend directory
```bash
cd backend
```

2. Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run the backend server
```bash
uvicorn app.main:app --reload
```

### Frontend Setup
1. Navigate to the frontend directory
```bash
cd frontend
```

2. Install dependencies
```bash
npm install
```

3. Start the React development server
```bash
npm start
```

## CSV Transaction Upload Format
Your CSV should have the following columns:
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

## License
MIT License
