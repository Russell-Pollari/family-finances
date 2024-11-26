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
        Detect which columns might correspond to date, amount, and description
        based on content analysis.
        """
        column_mapping = {}
        
        # Try to find date column
        for col in self.df.columns:
            try:
                # Try to parse the first non-null value as a date
                first_valid = self.df[col].dropna().iloc[0]
                parser.parse(str(first_valid))
                column_mapping['date'] = col
                break
            except (ValueError, TypeError):
                continue
                
        # Try to find amount column (numeric values)
        for col in self.df.columns:
            if col in column_mapping.values():
                continue
            if self.df[col].dtype in ['float64', 'int64'] or \
               self.df[col].str.replace('$', '').str.replace(',', '').str.replace('-', '').str.isnumeric().all():
                column_mapping['amount'] = col
                break
                
        # Assume the longest text column might be description
        text_lengths = {}
        for col in self.df.columns:
            if col in column_mapping.values():
                continue
            if self.df[col].dtype == 'object':
                avg_length = self.df[col].str.len().mean()
                text_lengths[col] = avg_length
        
        if text_lengths:
            description_col = max(text_lengths.items(), key=lambda x: x[1])[0]
            column_mapping['description'] = description_col
            
        return column_mapping
    
    def parse_transactions(self, column_mapping: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        Parse transactions using provided column mapping or auto-detect if none provided.
        """
        if column_mapping is None:
            column_mapping = self.detect_columns()
            
        transactions = []
        
        for _, row in self.df.iterrows():
            transaction = {}
            
            # Parse date
            if 'date' in column_mapping:
                date_str = str(row[column_mapping['date']])
                try:
                    transaction['date'] = parser.parse(date_str)
                except ValueError:
                    continue
                    
            # Parse amount
            if 'amount' in column_mapping:
                amount_str = str(row[column_mapping['amount']])
                # Remove currency symbols and commas
                amount_str = amount_str.replace('$', '').replace(',', '')
                try:
                    transaction['amount'] = float(amount_str)
                except ValueError:
                    continue
                    
            # Get description
            if 'description' in column_mapping:
                transaction['description'] = str(row[column_mapping['description']])
            else:
                # Use the first non-mapped column as description
                unused_cols = [col for col in self.df.columns if col not in column_mapping.values()]
                if unused_cols:
                    transaction['description'] = str(row[unused_cols[0]])
                else:
                    transaction['description'] = "Unknown"
                    
            # Add category if it exists
            if 'category' in column_mapping:
                transaction['category'] = str(row[column_mapping['category']])
                
            transactions.append(transaction)
            
        return transactions