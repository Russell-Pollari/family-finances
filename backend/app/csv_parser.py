import csv
from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd
from dateutil import parser


class CSVParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = pd.read_csv(file_path)

    def detect_columns(self) -> Dict[str, str]:
        """
        Detect which columns might correspond to date, credit, debit, and description
        based on content analysis.
        """
        column_mapping = {}
        columns = list(self.df.columns)

        # Try to find date column
        for col in columns:
            try:
                # Try to parse the first non-null value as a date
                first_valid = self.df[col].dropna().iloc[0]
                parser.parse(str(first_valid))
                column_mapping["date"] = col
                break
            except (ValueError, TypeError):
                continue

        def is_numeric_column(col):
            return (
                self.df[col].dtype in ["float64", "int64"]
                or self.df[col]
                .str.replace("$", "")
                .str.replace(",", "")
                .str.replace("-", "")
                .str.isnumeric()
                .all()
            )

        def check_adjacent_columns(start_idx, direction=1):
            """Check columns adjacent to the current one for numeric values"""
            idx = start_idx
            while 0 <= idx < len(columns):
                col = columns[idx]
                if col not in column_mapping.values() and is_numeric_column(col):
                    return col
                idx += direction
            return None

        # Try to find credit and debit columns (numeric values)
        for i, col in enumerate(columns):
            if col in column_mapping.values():
                continue

            # Check if it's a numeric column
            if is_numeric_column(col):
                col_lower = col.lower()
                if "credit" in col_lower or "deposit" in col_lower:
                    column_mapping["credit"] = col
                    # If this column is empty, check the next column
                    if self.df[col].isna().all():
                        next_col = check_adjacent_columns(i + 1)
                        if next_col:
                            column_mapping["credit"] = next_col
                elif "debit" in col_lower or "withdrawal" in col_lower:
                    column_mapping["debit"] = col
                    # If this column is empty, check the next column
                    if self.df[col].isna().all():
                        next_col = check_adjacent_columns(i + 1)
                        if next_col:
                            column_mapping["debit"] = next_col

        # If we still haven't found credit/debit columns, look for any numeric columns
        if "credit" not in column_mapping or "debit" not in column_mapping:
            numeric_cols = [col for col in columns if is_numeric_column(col) and col not in column_mapping.values()]
            if numeric_cols:
                if "credit" not in column_mapping and len(numeric_cols) > 0:
                    column_mapping["credit"] = numeric_cols[0]
                if "debit" not in column_mapping and len(numeric_cols) > 1:
                    column_mapping["debit"] = numeric_cols[1]

        # Assume the longest text column might be description
        text_lengths = {}
        for col in columns:
            if col in column_mapping.values():
                continue
            if self.df[col].dtype == "object":
                avg_length = self.df[col].str.len().mean()
                text_lengths[col] = avg_length

        if text_lengths:
            description_col = max(text_lengths.items(), key=lambda x: x[1])[0]
            column_mapping["description"] = description_col

        return column_mapping

    def parse_transactions(
        self, column_mapping: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Parse transactions using provided column mapping or auto-detect if none provided.
        """
        if column_mapping is None:
            column_mapping = self.detect_columns()

        transactions = []

        for _, row in self.df.iterrows():
            transaction = {}

            # Parse date
            if "date" in column_mapping:
                date_str = str(row[column_mapping["date"]])
                try:
                    transaction["date"] = parser.parse(date_str)
                except ValueError:
                    continue

            # Parse credit
            if "credit" in column_mapping:
                credit_str = str(row[column_mapping["credit"]])
                if pd.notna(credit_str) and credit_str.strip():
                    # Remove currency symbols and commas
                    credit_str = credit_str.replace("$", "").replace(",", "")
                    try:
                        transaction["credit"] = float(credit_str)
                    except ValueError:
                        transaction["credit"] = None
                else:
                    transaction["credit"] = None

            # Parse debit
            if "debit" in column_mapping:
                debit_str = str(row[column_mapping["debit"]])
                if pd.notna(debit_str) and debit_str.strip():
                    # Remove currency symbols and commas
                    debit_str = debit_str.replace("$", "").replace(",", "")
                    try:
                        transaction["debit"] = float(debit_str)
                    except ValueError:
                        transaction["debit"] = None
                else:
                    transaction["debit"] = None

            # Get description
            if "description" in column_mapping:
                transaction["description"] = str(row[column_mapping["description"]])
            else:
                # Use the first non-mapped column as description
                unused_cols = [
                    col for col in self.df.columns if col not in column_mapping.values()
                ]
                if unused_cols:
                    transaction["description"] = str(row[unused_cols[0]])
                else:
                    transaction["description"] = "Unknown"

            # Add category if it exists
            if "category" in column_mapping:
                transaction["category"] = str(row[column_mapping["category"]])

            transactions.append(transaction)

        return transactions
